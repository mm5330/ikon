const lock_btn = function ($button) {
    $button.prop("disabled", true);
}

const unlock_btn = function ($button) {
    $button.prop("disabled", false);
}

const show_prompt = function (text) {
    $("#confirm-msg").text(text)
}

/**
 * Encapsulated object for rendering JSON with format and color
 * it maintains the JSON container object and a json Editor object used to render JSON
 *
 * users can use getJSONString to get access to the valid JSON string, or null if this value is never set
 * setJSONString method is used to update the JSON content, and refresh the rendering part
 */
class JSONFormatter {
    constructor(containerID, editable = true) {
        this.$container = $(`#${containerID}`)
        this.$jsonEditor = new JsonEditor(`#${containerID}`)

        // only store valid JSON string
        this.jsonString = null
        this.jsonHTML = null
        if (!editable) {
            // Make the JSON formatter readonly
            this.$container.on("input", e => this.$container.html(this.jsonHTML));
        } else {
            // Format the container when the focus changes
            this.$container.on("blur", e => this.setJSONString(this.$container.text()));
        }
    }

    getJSONString() {
        return this.jsonString
    }

    setJSONString(text) {
        let jsonObj = null;
        try {
            jsonObj = JSON.parse(text)
        } catch {
            return false
        }
        this.$jsonEditor.load(jsonObj)
        this.jsonString = text
        this.jsonHTML = this.$container.html()
        return true;
    }
}



// Set initial placeholder for the script
const langScript = $("#script-content").text();
const deployCode = $("#script-deploy-code").text();

const jsonFormatter = new JSONFormatter("json-script-edit", true);
jsonFormatter.setJSONString(langScript);

const $confirmBtn = $("#editor-confirm");
const SCRIPT_EDIT_URL = '/script_edit';

// Submit button. send request to register API
$confirmBtn.click(function (e) {

    let text = jsonFormatter.getJSONString();

    // get form data, and check whether it's a valid json
    let script_json = null;
    try {
        script_json = { "script": JSON.parse(text.trim()), "deploy_code": deployCode };
    } catch (error) {
        show_prompt("Failed: Input is not in JSON format. Please try again");
        return;
    }
    // send out the register request
    lock_btn($confirmBtn);
    $.ajax({
        url: SCRIPT_EDIT_URL,
        type: "POST",
        data: JSON.stringify(script_json),
        contentType: "application/json",
        error: function (jqXHR, textStatus, errorThrown) {
            unlock_btn($confirmBtn);
            show_prompt(jqXHR.responseText);
        },
        success: function (data, textStatus, jqXHR) {
            unlock_btn($confirmBtn);
            show_prompt("Script updated successfully!");
        }
    });
});