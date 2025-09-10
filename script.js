async function procesar(accion) {
    const archivo = document.getElementById("archivo").files[0];
    const password = document.getElementById("password").value;
    const ascii = document.getElementById("ascii");

    if (!archivo || !password) {
        alert("Selecciona un archivo y escribe la contraseña");
        return;
    }

    const formData = new FormData();
    formData.append("archivo", archivo);
    formData.append("password", password);
    formData.append("accion", accion);

    try {
        // Apunta a la función serverless en /api/archivo
        const res = await fetch("/api/archivo", { method: "POST", body: formData });
        const data = await res.json();

        if (data.error) {
            alert("Error: " + data.error);
            return;
        }

        // Mostrar ASCII art si encripta
        if (accion === "encriptar") {
            ascii.textContent = `
███████╗ ██████╗ ██╗     ███████╗
██╔════╝██╔═══██╗██║     ██╔════╝
█████╗  ██║   ██║██║     █████╗  
██╔══╝  ██║   ██║██║     ██╔══╝  
███████╗╚██████╔╝███████╗███████╗
╚══════╝ ╚═════╝ ╚══════╝╚══════╝
Joel
`;
        } else {
            ascii.textContent = "";
        }

        // Convertir Base64 a bytes y descargar
        const bytes = Uint8Array.from(atob(data.filedata), c => c.charCodeAt(0));
        const blob = new Blob([bytes]);
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = data.filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
    } catch (err) {
        alert("Error al procesar el archivo: " + err);
    }
}
