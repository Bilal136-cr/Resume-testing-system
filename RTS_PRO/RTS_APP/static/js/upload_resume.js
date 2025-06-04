document.getElementById('resumeForm').addEventListener('submit', function(event) {
  const fileInput = document.getElementById('resumeInput');
  const errorMessage = document.getElementById('errorMessage');

  if (fileInput.files.length > 0) {
    const file = fileInput.files[0];
    const maxSize = 2 * 1024 * 1024; // 2MB in bytes

    if (file.size > maxSize) {
      event.preventDefault();  // Stop form submission
      errorMessage.textContent = "File size exceeds 2MB. Please choose a smaller file.";
    }
  }
});