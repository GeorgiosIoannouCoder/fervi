function showFileInput() {
    document.getElementById("fileInput").style.display = "block";
    document.getElementById("urlInput").style.display = "none";
    document.getElementById("urlInput").value = "";
}

function showURLInput() {
    document.getElementById("urlInput").style.display = "block";
    document.getElementById("fileInput").style.display = "none";
}

function enableClassifyButton() {
    const fileInput = document.getElementById("fileInput");
    const urlInput = document.getElementById("urlInput");
    const localSelected = document.querySelector('input[name="source"][value="local"]').checked;

    if (localSelected && fileInput.files.length > 0) {
        document.getElementById("btn-classify").disabled = false;
    } else if (!localSelected && urlInput.value.trim() !== "") {
        document.getElementById("btn-classify").disabled = false;
    } else {
        document.getElementById("btn-classify").disabled = true;
    }
}