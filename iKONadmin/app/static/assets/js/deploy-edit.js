const $createCreateBtn = $("#create-create");
const $createCancelBtn = $("#create-cancel");
const $editConfirmBtn = $("#edit-confirm");
const $editCancelBtn = $("#edit-cancel");

function disableCreateButton() {
    $createCreateBtn.prop("disabled", true);
    $createCancelBtn.prop("disabled", true);
}

function disableEditButton() {
    $editConfirmBtn.prop("disabled", true);
    $editCancelBtn.prop("disabled", true);
}

//
// $createCreateBtn.click(function (e) {
//     disableCreateButton();
// });
//
// $createCancelBtn.click(function (e) {
//     disableCreateButton();
// });
//
// $editConfirmBtn.click(function (e) {
//     disableEditButton();
// });
//
// $editCancelBtn.click(function (e) {
//     disableEditButton();
// });
