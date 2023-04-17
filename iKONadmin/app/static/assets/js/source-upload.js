const reader = new FileReader();

const lock_btn = function ($button) {
    $button.prop("disabled", true);
}

const unlock_btn = function ($button) {
    $button.prop("disabled", false);
}

const show_prompt = function (text) {
    $("#uploadMsg").text(text)
}

const $source_file = $("#sourceFile")
let source_data = ""
reader.onload = function (file) {
    source_data = file.target.result;
    displayPreview();
};

$source_file.change(function (e) {
    let files = e.target.files;
    if (files.length === 1) {
        reader.readAsText(files[0]);
    } else {
        show_prompt("Failed: Please choose ONE File.");
    }
});

const $uploadBtn = $("#sourceUpload");
const SOURCE_UPLOAD_URL = '/source_upload';

const $previewTbl = $("#previewTable")
function displayPreview() {
    $uploadBtn.prop("disabled", false);  // re-enable upload button
    show_prompt("")  // clear prompt
	let table_body = "";
	const data = source_data.split("\n");
    let data_head = data[0].split(",");
    if (data_head.length !== 2 || data_head[0] !== "year" || data_head[1] !== "value") {
        $uploadBtn.prop("disabled", true);
        show_prompt("Failed: Mismatched header in the csv file. Please double check your file is formatted properly.");
        $previewTbl.html("");
        return;
    }
	for (let i = 1; i < data.length; i++) {
		table_body += "<tr>";
		const row = data[i];
		const cells = row.split(",");

		for (let j = 0; j < cells.length; j++) {
			table_body += "<td>";
			table_body += cells[j];
			table_body += "</td>";
		}
		table_body += "</tr>";
	}
	$previewTbl.html(table_body);
}


$uploadBtn.click(function (e) {
    const source_name = $("#sourceName").val();
    const source_type = $("#sourceType").val();
    const source_country = $("#sourceCountry").val();
    const source_region = $("#sourceRegion").val();
    const source_description = $("#sourceDescription").val();
    if (source_name.length === 0) {
        show_prompt("Failed: Please fill the 'Data source name' field",);
        return;
    }
    let script_json = { "source_data": source_data.trim(),
        "source_name": source_name, "source_type": source_type,
        "source_country": source_country, "source_region": source_region,
        "source_description": source_description};
    lock_btn($uploadBtn);
    $.ajax({
        url: SOURCE_UPLOAD_URL,
        type: "POST",
        data: JSON.stringify(script_json),
        contentType: "application/json",
        error: function (jqXHR, textStatus, errorThrown) {
            unlock_btn($uploadBtn);
            show_prompt(jqXHR.responseText);
        },
        success: function (data, textStatus, jqXHR) {
            unlock_btn($uploadBtn);
            show_prompt("Data source uploaded successfully!");
        }
    });
});