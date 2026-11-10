import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = process.cwd();
const SKILL_DIR = "C:/Users/Lenovo/.codex/plugins/cache/openai-primary-runtime/presentations/26.1105.12137/skills/presentations";
const RUNTIME_PYTHON = "C:/Users/Lenovo/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe";
const buildDir = path.join(workspaceDir, "build", "presentation");
const FINAL_PPTX = path.join(workspaceDir, "presentation", "toxic_comment_detection_presentation.pptx");

const colors = { navy: "#12304A", blue: "#1F5D8C", sky: "#EAF3F8", ink: "#15202B", muted: "#56616B", pale: "#F6F9FB", red: "#B54242" };
const page = { left: 78, top: 58, width: 1124, height: 604 };

async function writeBlob(filePath, blob) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

function box(slide, text, position, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    fontFamily: "Aptos",
    fontSize: 20,
    color: colors.ink,
    ...style,
  };
  return shape;
}

function title(slide, value, subtitle = "") {
  box(slide, value, { left: page.left, top: page.top, width: page.width, height: 56 }, { fontFamily: "Aptos Display", fontSize: 34, bold: true, color: colors.navy });
  if (subtitle) box(slide, subtitle, { left: page.left, top: page.top + 62, width: page.width, height: 30 }, { fontSize: 15, color: colors.muted });
}

function footer(slide, value = "Applied Artificial Intelligence | Final Project") {
  box(slide, value, { left: page.left, top: 679, width: page.width, height: 18 }, { fontSize: 10, color: colors.muted });
}

function bulletLines(slide, lines, left, top, width, fontSize = 21) {
  lines.forEach((line, index) => {
    box(slide, `• ${line}`, { left, top: top + index * 55, width, height: 45 }, { fontSize, color: colors.ink });
  });
}

function label(slide, value, left, top, width) {
  box(slide, value.toUpperCase(), { left, top, width, height: 24 }, { fontSize: 12, bold: true, color: colors.blue });
}

async function main() {
  const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });

  // 1. Cover
  {
    const slide = presentation.slides.add();
    slide.background.fill = colors.pale;
    label(slide, "Final Project", page.left, 118, 250);
    box(slide, "Toxic Comment\nDetection", { left: page.left, top: 164, width: 680, height: 180 }, { fontFamily: "Aptos Display", fontSize: 55, bold: true, color: colors.navy });
    box(slide, "Binary text classification with imbalance-aware evaluation", { left: page.left, top: 370, width: 710, height: 45 }, { fontSize: 24, color: colors.muted });
    box(slide, "Team members and group: replace before submission", { left: page.left, top: 548, width: 650, height: 30 }, { fontSize: 18, color: colors.ink });
    box(slide, "Data source: Jigsaw Toxic Comment Classification Challenge on Kaggle", { left: page.left, top: 592, width: 790, height: 25 }, { fontSize: 13, color: colors.muted });
  }

  // 2. Problem and data
  {
    const slide = presentation.slides.add();
    slide.background.fill = "white";
    title(slide, "Problem and dataset", "Classify each comment as toxic or non-toxic");
    label(slide, "Task", page.left, 150, 180);
    bulletLines(slide, [
      "Input: English Wikipedia discussion comments",
      "Target: toxic label, 1 for toxic and 0 for non-toxic",
      "Challenge: toxic comments form the minority class",
    ], page.left, 185, 540, 21);
    label(slide, "Data fields", 720, 150, 220);
    bulletLines(slide, [
      "comment_text for model input",
      "id for data integrity and database joins",
      "Six labels retained for later analysis",
    ], 720, 185, 430, 20);
    box(slide, "Official file: train.csv from Kaggle. The synthetic sample in the repository is only a pipeline smoke test.", { left: page.left, top: 455, width: page.width, height: 58 }, { fontSize: 18, color: colors.red, italic: true });
    footer(slide);
  }

  // 3. Workflow
  {
    const slide = presentation.slides.add();
    slide.background.fill = colors.pale;
    title(slide, "Project workflow", "A repeatable path from raw data to model evidence");
    const steps = [
      ["1", "Validate CSV", "Required columns, missing text, labels"],
      ["2", "Create SQLite", "Comments, runs, predictions"],
      ["3", "Train models", "Stratified split, class weights"],
      ["4", "Evaluate", "ROC-AUC, PR-AUC, F1, matrix"],
      ["5", "Inspect errors", "False positives and false negatives"],
    ];
    steps.forEach(([number, heading, detail], index) => {
      const left = page.left + index * 222;
      box(slide, number, { left, top: 190, width: 38, height: 42 }, { fontSize: 30, bold: true, color: colors.blue });
      box(slide, heading, { left, top: 244, width: 190, height: 46 }, { fontSize: 20, bold: true, color: colors.navy });
      box(slide, detail, { left, top: 306, width: 190, height: 76 }, { fontSize: 16, color: colors.muted });
    });
    box(slide, "Console entry point: python -m src.cli", { left: page.left, top: 498, width: 620, height: 36 }, { fontSize: 22, bold: true, color: colors.navy });
    footer(slide);
  }

  // 4. Models
  {
    const slide = presentation.slides.add();
    slide.background.fill = "white";
    title(slide, "Compared models", "Both models use Logistic Regression with balanced class weights");
    label(slide, "Baseline", page.left, 165, 260);
    box(slide, "Word TF-IDF", { left: page.left, top: 202, width: 420, height: 50 }, { fontSize: 30, bold: true, color: colors.navy });
    bulletLines(slide, ["Word 1-2 grams", "Sublinear term frequency", "Transparent coefficients"], page.left, 276, 420, 19);
    label(slide, "Comparison model", 680, 165, 330);
    box(slide, "Word plus character TF-IDF", { left: 680, top: 202, width: 460, height: 50 }, { fontSize: 29, bold: true, color: colors.navy });
    bulletLines(slide, ["Word 1-2 grams", "Character-within-word 3-5 grams", "Captures spelling variants and fragments"], 680, 276, 450, 19);
    box(slide, "The model with the highest held-out ROC-AUC becomes best_model.joblib.", { left: page.left, top: 500, width: page.width, height: 35 }, { fontSize: 20, color: colors.blue, bold: true });
    footer(slide);
  }

  // 5. Evaluation
  {
    const slide = presentation.slides.add();
    slide.background.fill = colors.pale;
    title(slide, "Evaluation for class imbalance", "Accuracy alone can hide poor toxic-comment detection");
    label(slide, "Primary metric", page.left, 165, 220);
    box(slide, "ROC-AUC", { left: page.left, top: 205, width: 320, height: 48 }, { fontSize: 34, bold: true, color: colors.navy });
    box(slide, "Measures whether toxic comments receive higher scores than non-toxic comments across all thresholds.", { left: page.left, top: 275, width: 390, height: 100 }, { fontSize: 19, color: colors.ink });
    label(slide, "Threshold evidence", 600, 165, 260);
    bulletLines(slide, ["Precision: how many flagged comments are toxic", "Recall: how many toxic comments are detected", "F1: balance of precision and recall", "Confusion matrix at 0.50 threshold"], 600, 205, 540, 19);
    box(slide, "The final report must use the official-data metrics generated in artifacts/metrics.json.", { left: page.left, top: 500, width: page.width, height: 34 }, { fontSize: 19, color: colors.red, italic: true });
    footer(slide);
  }

  // 6. SQLite
  {
    const slide = presentation.slides.add();
    slide.background.fill = "white";
    title(slide, "SQLite analysis layer", "Data, model runs, and test predictions remain queryable");
    label(slide, "Schema", page.left, 160, 180);
    box(slide, "comments", { left: page.left, top: 215, width: 270, height: 44 }, { fontSize: 28, bold: true, color: colors.navy });
    box(slide, "comment_id, text, toxic labels, length", { left: page.left, top: 270, width: 330, height: 55 }, { fontSize: 18, color: colors.muted });
    box(slide, "model_runs", { left: 470, top: 215, width: 270, height: 44 }, { fontSize: 28, bold: true, color: colors.navy });
    box(slide, "model, vectorizer, ROC-AUC, F1, time", { left: 470, top: 270, width: 330, height: 55 }, { fontSize: 18, color: colors.muted });
    box(slide, "predictions", { left: 870, top: 215, width: 270, height: 44 }, { fontSize: 28, bold: true, color: colors.navy });
    box(slide, "actual label, prediction, probability", { left: 870, top: 270, width: 300, height: 55 }, { fontSize: 18, color: colors.muted });
    label(slide, "Eight SQL queries", page.left, 420, 260);
    bulletLines(slide, ["Class balance and comment-length summaries", "Experiment leaderboard and confusion-matrix cells", "High-confidence false positives and false negatives", "CTE and window-function model ranking"], page.left, 456, 1060, 18);
    footer(slide);
  }

  // 7. Results plan
  {
    const slide = presentation.slides.add();
    slide.background.fill = colors.pale;
    title(slide, "Results to present after the official run", "Never report the synthetic sample as final-model evidence");
    label(slide, "Generated files", page.left, 165, 240);
    bulletLines(slide, ["comparison.csv with both model metrics", "metrics.json for the selected model", "roc_curve.png and confusion_matrix.png", "best_model.joblib for custom predictions"], page.left, 205, 520, 19);
    label(slide, "Discussion points", 720, 165, 240);
    bulletLines(slide, ["Which model has higher ROC-AUC?", "Where does the confusion matrix show risk?", "Which errors need moderation review?", "Would a different threshold fit the use case?"], 720, 205, 420, 19);
    box(slide, "Run: python -m src.cli compare --data data/raw/train.csv", { left: page.left, top: 500, width: page.width, height: 38 }, { fontSize: 21, bold: true, color: colors.navy });
    footer(slide);
  }

  // 8. Conclusion
  {
    const slide = presentation.slides.add();
    slide.background.fill = "white";
    title(slide, "Conclusion and team contribution", "A reproducible baseline that can be extended with a transformer experiment");
    label(slide, "Conclusion", page.left, 165, 180);
    bulletLines(slide, ["The project makes imbalance visible through class weights and suitable metrics", "The comparison tests whether character features add value", "SQLite supports repeatable quantitative and qualitative analysis"], page.left, 205, 1030, 20);
    label(slide, "Contribution statement", page.left, 425, 250);
    box(slide, "Replace with real member names, groups, and responsibilities before submission. Each member should be ready to explain the code and results during the defense.", { left: page.left, top: 463, width: 1040, height: 60 }, { fontSize: 20, color: colors.red, italic: true });
    footer(slide);
  }

  await fs.mkdir(buildDir, { recursive: true });
  for (const [index, slide] of presentation.slides.items.entries()) {
    await writeBlob(path.join(buildDir, `slide-${String(index + 1).padStart(2, "0")}.png`), await presentation.export({ slide, format: "png", scale: 1 }));
  }

  const { finalizePresentation } = await import(pathToFileURL(path.join(SKILL_DIR, "container_tools/artifact_tool_utils.mjs")).href);
  const stagingDir = path.join(workspaceDir, ".codex-finalizer");
  const candidatePath = path.join(stagingDir, "toxic_comment_detection_candidate.pptx");
  await fs.mkdir(stagingDir, { recursive: true });
  await fs.mkdir(path.dirname(FINAL_PPTX), { recursive: true });
  await (await PresentationFile.exportPptx(presentation)).save(candidatePath);
  const result = await finalizePresentation({
    workspaceDir,
    candidatePath,
    finalPath: FINAL_PPTX,
    pythonExecutable: RUNTIME_PYTHON,
    integrityValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_package_integrity.py"),
    layoutValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_layout_geometry.py"),
    layoutArgs: ["--expected-slide-size-emu", "12192000,6858000", "--validate-heading-fit"],
    // The bundled renderer resolves the requested Office fonts to Arial in the exported file.
    fontPolicy: { basis: "design", families: ["Arial"] },
    verifyArtifactToolImport: true,
    receiptPath: path.join(stagingDir, "presentation.validation.json"),
  });
  console.log(JSON.stringify({ finalPath: FINAL_PPTX, result }, null, 2));
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
