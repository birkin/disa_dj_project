

let SETTINGS;

// STEVE'S CODE (not used, but keep for reference while under dev)

// Form initialization functions

function makeCitationFieldInput(fieldData) {
  const $row = $("<li/>", {
    class: "citation-field",
    style: `order: ${fieldData.rank}`,
  });

  const $input = $("<input/>", {
    id: fieldData.name,
    class: "form-control",
    type: "text",
    placeholder: fieldData.display,
    "data-citation-field": fieldData.name,
  });

  $input.val(fieldData.value);
  $row.append($input);

  return $row;
}

function updateCitationFields(citeData, citeType, ctMap) {
  const ct_fields = ctMap[citeType],
    $fg = $("#citation_fields");

  $("#citation_fields").siblings("label").show();
  $fg.empty();

  for (let i = 0; i < ct_fields.length; i++) {
    let field_data = ct_fields[i];
    if (field_data.name in citeData) {
      field_data["value"] = citeData[field_data.name];
    } else {
      field_data["value"] = "";
    }
    $fg.append(makeCitationFieldInput(field_data));
  }
}

function collectCitationFieldData(dataObj) {
  const cite_fields = $(".citation-field");
  dataObj["fields"] = {};
  cite_fields.each(function (_) {
    $input = $(this).find("input");
    dataObj.fields[$input.attr("data-citation-field")] = $input.val();
  });
  return dataObj;
}

function setInputValues(docData) {
  if ($.isEmptyObject(docData)) {
    return;
  }
  $("#citation").text(docData["citation"]);
  $("#document_type").val(docData["citation_type_id"]).attr("selected", true);
  $("#comments").text(docData["comments"]);
  $("#acknowledgements").text(docData["acknowledgements"]);
}

function collectInputValues() {
  let data = {};
  data["citation_type_id"] = Number($("#document_type").val());
  data["comments"] = $("#comments").val();
  data["acknowledgements"] = $("#acknowledgements").val();
  data = collectCitationFieldData(data);
  return data;
}

// BELOW @todo - may want to move this message to
//   a <template> element

function setFormHeader(docData) {
  const header = $("#document_header");
  console.log("in setFormHeader; header, ", header);
  if ($.isEmptyObject(docData)) {
    header.text("Add a document");
    header.append(`
      <div style="font-size: 50%">
        <em>
            Fill out this form only when entering a document for the first time.
            If your document has been already entered, find your document in the
            <a href="/editor">recent document list</a> and add an item. 
        </em>
      </div>`);
    $("#doc_update").text("Create");
    $("#citation_fields").siblings("label").hide();
  } else {
    header.text(docData["citation"]);
  }
}

function initializeForm(data, ctMap) {
  console.log("starting initializeForm()");
  setFormHeader(data["doc"]);
  addTypeOptions(data["doc_types"]);
  setInputValues(data["doc"]);
  if ("fields" in data["doc"]) {
    updateCitationFields(
      data["doc"]["fields"],
      data["doc"]["citation_type_id"],
      ctMap
    );
  }
}

function readDocumentData(docId, ctMap, copy) {
  console.log("starting readDocumentData()");
  let doc_data_api;
  if (copy) {
    doc_data_api = SETTINGS.docDataApi.copy;
    console.log("in readDocumentData; doc_data_api for `copy`, ", doc_data_api);
  } else if (docId) {
    doc_data_api = SETTINGS.docDataApi.docId.replace('STUB', docId);
    console.log(
      "in readDocumentData; doc_data_api with `docId`, ",
      doc_data_api
    );
  } else {
    doc_data_api = SETTINGS.docDataApi.noDocId;
    console.log(
      "in readDocumentData; doc_data_api with NO `docId`, ",
      doc_data_api
    );
  }
  console.log("in readDocumentData; docId, ", docId);
  console.log("in readDocumentData; copy, ", copy);
  $.get(doc_data_api, function (data) {
    initializeForm(data, ctMap);
  });
}

// FORM SAVING FUNCTIONS

// Main save function
// Called when #doc-update is clicked

function updateDocumentData(docId, ctMap) {
  let doc_data_api;
  if (docId) {
    doc_data_api = SETTINGS.docDataApi.docId.replace('STUB', docId);
    // doc_data_api = "{% url 'data_documents_url' 'STUB' %}".replace('STUB', docId);
    console.log(
      "in updateDocumentData; doc_data_api with `docId`, ",
      doc_data_api
    );
  } else {
    doc_data_api = SETTINGS.docDataApi.noDocId;
    // doc_data_api = "{% url 'data_documents_url' %}";
    console.log(
      "in updateDocumentData; doc_data_api with NO `docId`, ",
      doc_data_api
    );
  }
  var data = collectInputValues();
  var method = docId ? 'PUT' : 'POST';
  $.ajax({
    type: method,
    url: doc_data_api,
    contentType: "application/json",
    data: JSON.stringify(data),
    success: function (data) {
      if (method === "POST") {
        window.location.href = data.redirect;
      } else {
        initializeForm(data, ctMap);
        $("#document_form").accordion("option", "active", false);
      }
    },
  });
}

function activateReferenceDelete($delBtn) {
  const $cancel_btn = $("<button/>", {
    class: "btn btn-secondary deactivate-delete",
    title: "Cancel current changes",
  });
  const $cancel_span = $("<span/>", { class: "fas fa-undo" });
  $cancel_btn.append($cancel_span);
  $delBtn.empty().text("Confirm delete").addClass("active");
  $delBtn.before($cancel_btn);
  return true;
}

function deactivateReferenceDelete($cancelBtn) {
  const $del_span = $("<span/>", { class: "fas fa-times-circle" });
  const $del_btn = $cancelBtn.next(".del-reference");
  $cancelBtn.remove();
  $del_btn.empty().append($del_span).removeClass("active");
  return true;
}

function deleteReference($refRow, ctMap) {
  const ref_del_api = SETTINGS.ref_del_api.replace(
    'STUB',
    $refRow.attr("data-reference")
  );
  console.log("in deleteReference; ref_del_api, ", ref_del_api);
  $.ajax({
    type: "DELETE",
    url: ref_del_api,
    success: (data) => (window.location.href = data.redirect),
  });
}

function deleteDocument(doc_id) {
  /*  This only passes the doc_id; think about passing more identifying info
  ...so the server doesn't have to do a lookup for more document info. */
  console.log("in `var deleteDocument`; `doc_id`, ", doc_id);
  // var doc_data_api_root = "{% url 'data_documents_url' %}";
  const doc_data_api_root = SETTINGS.docDataApi.root,
    full_doc_data_api = `${doc_data_api_root}${doc_id}/`;
  $.ajax({
    type: "DELETE",
    url: full_doc_data_api,
    success: function (data) {
      // setTimeout( () => {console.log("waiting two seconds");}, 5000 );
      console.log("in deleteDocument; data, ", data);
      window.location.href = data.redirect;
      // alert( "Citation " + doc_id + " marked for deletion." );
    },
  });
  console.log("ajax call done");
}

// STEVE'S MAIN

function steve_main() {
  const doc_id = SETTINGS.doc_id;
  console.log("in document.ready(); doc_id, ", doc_id);
  const cite_type_fields = SETTINGS.cite_type_fields;
  // var cite_type_fields = JSON.parse('{{ ct_fields_json | safe }}');
  console.log("in document.ready(); cite_type_fields, ", cite_type_fields);
  console.log("in document.ready(); about to call readDocumentData()");
  readDocumentData(doc_id, cite_type_fields, false);
  console.log("in document.ready(); called readDocumentData()");
  // var documents_url = "{{ documents_url }}";
  const documents_url = SETTINGS.documents_url;
  // var documents_url = "{% url 'editor_index_url' %}";
  console.log("in document.ready(); documents_url, ", documents_url);

  $("#document_form").accordion({
    collapsible: true,
    header: "h2",
    heightStyle: "content",
    active: doc_id ? false : 0,
  });
  $("#document_date").datepicker({
    changeMonth: true,
    changeYear: true,
    yearRange: "1492:1900",
  });
  $("#document_type").on("change", function (e) {
    e.preventDefault();
    const cite_type = $(this).val(),
      cite_data = collectCitationFieldData({});
    updateCitationFields(cite_data["fields"], cite_type, cite_type_fields);
  });
  $("#references_table").on(
    "click",
    ".del-reference:not(.active)",
    function (e) {
      e.preventDefault();
      activateReferenceDelete($(this));
    }
  );
  $("#references_table").on("click", ".deactivate-delete", function (e) {
    e.preventDefault();
    deactivateReferenceDelete($(this));
  });
  $("#references_table").on("click", ".del-reference.active", function (e) {
    e.preventDefault();
    var $ref_row = $(this).closest("tr");
    deleteReference($ref_row, cite_type_fields);
  });
  $("#doc_update").on("click", function (e) {
    e.preventDefault();
    updateDocumentData(doc_id, cite_type_fields);
  });
  $("#copy_previous").on("click", function (e) {
    e.preventDefault();
    $(this).parent().remove();
    readDocumentData(doc_id, cite_type_fields, true);
  });

  if (SETTINGS.can_delete_doc) {
    $("#confirm-delete-button").on("click", function (e) {
      e.preventDefault();
      deleteDocument(doc_id);
      window.location.replace(documents_url);
    });
  }
}

// PATRICK'S CODE

// FORM INITIALIZATION

// Initialize citation type dropdown

function initializeCitationTypeDropdown(SETTINGS) {
  
  const docTypeDropdownElem = document.getElementById(SETTINGS.DOC_TYPE_ELEM_ID);

  if (docTypeDropdownElem) {
    for (const [name, index] of Object.entries(SETTINGS.DOC_TYPES)) {
      const dropDownItem = document.createElement('option');
      dropDownItem.value = index;
      dropDownItem.text = name;
      dropDownItem.selected = index === SETTINGS.citation_data.citation_type_id;
      docTypeDropdownElem.append(dropDownItem);
    }
  }
}

// Get callback for when the citation type dropdown changes

function getCitationFieldUpdateCallback() {
  // Load a bunch of form elements

  const requiredFieldsContainer = document.getElementById("required-fields"),
    requiredFieldsHeader = document.getElementById("required-fields-header"),
    optionalFieldsContainer = document.getElementById("optional-fields"),
    optionalFieldsHeader = document.getElementById("optional-fields-header"),
    hiddenFieldsContainer = document.getElementById("hidden-fields"),
    citationTypeSelector = document.getElementById('document_type'),
    citationFields = Array.from(
      document.getElementsByClassName("citation-field")
    );

  // Return callback

  return () => {
    const citationTypeId = parseInt(citationTypeSelector.value),
      fieldStatus = SETTINGS.FIELDS_BY_DOC_TYPE[citationTypeId];

    // Move citation fields to required / optional / hidden

    citationFields.forEach((citationField) => {
      const citationFieldId = citationField.id;

      if (fieldStatus.required.includes(citationFieldId)) {
        requiredFieldsContainer.appendChild(citationField);
      } else if (fieldStatus.optional.includes(citationFieldId)) {
        optionalFieldsContainer.appendChild(citationField);
      } else {
        hiddenFieldsContainer.appendChild(citationField);
      }
    });

    // Unhide

    requiredFieldsHeader.removeAttribute("hidden");
    optionalFieldsHeader.removeAttribute("hidden");
  };
}

// Initialize form fields with DB values
// Note that form IDs must match data object property
//  names (e.g. for property 'abc', the input field would be
//  'abc-value')

function initFormFields(citationData) {
  // Citation bib fields
  Object.keys(citationData.citation_type_fields).forEach(
    (fieldId) => 
      (document.getElementById(`${fieldId}-value`).value =
        citationData.citation_type_fields[fieldId])
  );

  // Acknowledgements
  document.getElementById("formInputDISAAcknowledgements").value =
    citationData.acknowledgements;
  // MORE TO COME ...
}

// FORM SUBMISSION

// postData() from https://tinyurl.com/kd39rkq

async function postData(url = '', data = {}) {
  const response = await fetch(url, {
    method: 'POST',
    mode: 'same-origin', // no-cors, *cors, same-origin
    cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
    credentials: 'same-origin', // include, *same-origin, omit
    headers: { 'Content-Type': 'application/json' },
    redirect: 'follow', // manual, *follow, error
    referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
    body: JSON.stringify(data) // body data type must match "Content-Type" header
  });
  return response.json(); // parses JSON response into native JavaScript objects
}

function onCitationFormSubmit() {

  const CITATION_API_URL = 'http://example.com', // Should be a setting
        formFields = Array.from(
          document.querySelectorAll(`#citation-form *[id$='-value']`)
        );
  
  const citationData = formFields.reduce((citDataElem, currCitDataElem) => {
    const citDataFieldName = currCitDataElem.id.replace('-value', ''),
          citDataFieldValue = currCitDataElem.value;
    citDataElem[citDataFieldName] = citDataFieldValue;
    return citDataElem;
  }, {});

  console.log('SUBMITTING CITATION DATA', citationData);

  /* AWAITING IMPLEMENTATION
  postData(CITATION_API_URL, citationData)
  .then(data => {
    console.log(data);
  }); */

  return false;
}

// MAIN

function main(S) {
  
  SETTINGS = S;

  document.addEventListener("DOMContentLoaded", () => {

    const ageByNumberCheckbox = document.getElementById(
      SETTINGS.AGE_BY_NUMBER_CHECKBOX_ID
    );

    if (ageByNumberCheckbox) {
      ageByNumberCheckbox.onchange = function (e) {
        const classOp = this.checked ? "add" : "remove";
        document.body.classList[classOp](
          SETTINGS.AGE_BY_NUMBER_DISPLAY_CSS_CLASS
        );
      };
    }

    // Initialize the form fields with data from the DB

    initializeCitationTypeDropdown(SETTINGS);
    initFormFields(SETTINGS.citation_data);

    // Add listener for citation type dropdown selector

    const updateCitationFieldVisibility = getCitationFieldUpdateCallback();
    document.getElementById('document_type').addEventListener(
      "change",
      updateCitationFieldVisibility
    );

    updateCitationFieldVisibility();

    // Handlers for form submission
    document.getElementById('citation-form-submit')
            .addEventListener('click', onCitationFormSubmit);

  });
}

export { main };
