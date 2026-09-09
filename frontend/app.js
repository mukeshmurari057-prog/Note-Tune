const files = document.querySelector("#files");
const button = document.querySelector("#make-song");
const status = document.querySelector("#status");
const result = document.querySelector("#result");
const lyrics = document.querySelector("#lyrics");
const coverage = document.querySelector("#coverage");
let latestLyrics = "";

button.addEventListener("click", async () => {
  if (!files.files.length) {
    status.textContent = "Please choose at least one file.";
    return;
  }
  const body = new FormData();
  [...files.files].forEach(file => body.append("files", file));
  button.disabled = true;
  status.textContent = "Reading your notes and writing a song...";
  try {
    const response = await fetch("http://127.0.0.1:8000/api/process", { method: "POST", body });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Something went wrong.");
    latestLyrics = data.lyrics;
    lyrics.textContent = latestLyrics;
    coverage.textContent = `${data.coverage.covered}/${data.coverage.total} concepts covered` +
      (data.coverage.passed ? " — complete!" : " — review the missing details below.");
    result.classList.remove("hidden");
    status.textContent = "Done!";
  } catch (error) {
    status.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});

document.querySelector("#download").addEventListener("click", () => {
  const blob = new Blob([latestLyrics], { type: "text/plain" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "notetune-song.txt";
  link.click();
  URL.revokeObjectURL(link.href);
});

