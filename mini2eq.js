const uploadInput = document.getElementById('file');

uploadInput.addEventListener("change", () => {
    var file = uploadInput.files[0];
    var reader = new FileReader();
    reader.readAsText(file);

    reader.onload = function (e) {
        document.getElementById("originalContent").textContent = e.target.result;
        
        //clear the eq-bands dropdown selector except for the "all" option

        var length = document.getElementById("eq-bands").options.length;
        for (i = length - 1; i > 0; i--)
            document.getElementById("eq-bands").options[i] = null;
    
        //add the number of values in hertz_db to the eq-bands dropdown selector
    
        for (var i = 0; i < calibration_data(e.target.result).length; i++) {
            var option = document.createElement("option");
            option.text = i + 1;
            option.value = i + 1;
            document.getElementById("eq-bands").add(option);
        }

        main(e.target.result);
    };

    reader.onerror = function (e) {
        alert("Error: " + e.target.error.name);
        return;
    };
}, false);

document.getElementById("eq-bands").addEventListener("change", () => {
    var file = uploadInput.files[0];
    var reader = new FileReader();
    reader.readAsText(file);

    reader.onload = function (e) {
        document.getElementById("originalContent").textContent = e.target.result;
        main(e.target.result);
    };
}, false);

function download_preset() {
    var reader = new FileReader();
    reader.readAsText(uploadInput.files[0]);
    var fileName = uploadInput.files[0].name;
    // now change the filename to be the original file, but with -(format) appended before the extension
    fileName = fileName.replace(/\.[^/.]+$/, "") + "-" + document.getElementById("format").value + ".txt";

    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(eq_preset));
    element.setAttribute('download', fileName);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}

function main(fileContent) {
    hertz_db = calibration_data(fileContent);

    bands = document.getElementById("eq-bands").value;

    if (bands == "all")
        bands = hertz_db.length;

    hertz_per_band = hertz_db.length / bands;

    new_hertz_db = [];

    for (var i = 0; i < bands; i++) {
        average_hertz = 0;
        average_db = 0;

        for (var j = 0; j < hertz_per_band; j++) {
            average_hertz += hertz_db[Math.floor(i * hertz_per_band) + j][0];
            average_db += hertz_db[Math.floor(i * hertz_per_band) + j][1];
        }

        average_hertz /= hertz_per_band;
        average_db /= hertz_per_band;

        new_hertz_db.push([average_hertz, average_db]);
    }

    hertz_db = new_hertz_db;

    output_format = document.getElementById("format").value;

    if (output_format == "apo")
        eq_preset = generate_apo(new_hertz_db);

    document.getElementById("eqContent").textContent = eq_preset;
}

function calibration_data(file) {
    lines = [];
    hertz_db = [];

    lines = file.split(/\r?\n/);

    for (var i = 0; i < lines.length; i++) {
        if (lines[i].charAt(0) == "\"" || lines[i].charAt(0).match(/[a-z]/i) || lines[i].charAt(0) == "")
            continue;

        hertz_db.push(lines[i].split(/\s+/));
    }

    for (var i = 0; i < hertz_db.length; i++) {
        hertz_db[i][0] = parseFloat(hertz_db[i][0]);
        hertz_db[i][1] = parseFloat(hertz_db[i][1]);
    }

    return hertz_db;
}

function generate_apo(data) {
    content = "";
    for (var i = 0; i < data.length; i++) {
        previous = null;
        next = null;

        if (i > 0)
            previous = data[i - 1][0];
        if (i < data.length - 1)
            next = data[i + 1][0];

        q = q_setting(previous, data[i][0], next);

        content = content.concat("Filter: " + (i + 1) + " ON PK Fc " + data[i][0] + " Hz Gain " + data[i][1] + " dB Q " + q + "\n");
    }
    return content;
}

function q_setting(previous, current, next) {
    if (previous == null)
        return current / (next - current);

    if (next == null)
        return current / (current - previous);

    return current / (next - previous);
}