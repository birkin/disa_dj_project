

// UUID generator
// Source: https://stackoverflow.com/questions/105034/how-to-create-a-guid-uuid/2117523#2117523

function uuidv4() {
  return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
  );
}

// Parse URL for item and/or person to display
//  URL format: <url><DOC ID>/#/<ITEM ID>/<PERSON ID>

function getRoute() {
  const [itemId, personId] = window.location.hash.replace(/^[#\/]+/, '').split('/');
  return { 
    itemId: parseInt(itemId) || undefined,
    personId: parseInt(personId) || undefined
  };
}

// Get callback for change in source type
// (it's a callback in order to bake in the dataAndSettings object)

function getUpdateCitationFieldVisibilityCallback(FIELDS_BY_DOC_TYPE) {

  const requiredFieldsHeader = document.getElementById('required-fields-header'),
        optionalFieldsHeader = document.getElementById('optional-fields-header');

  return function(citationTypeId) {

    const citationFields = document.querySelectorAll('#citation-fields > div'),
          fieldStatus = FIELDS_BY_DOC_TYPE[citationTypeId];

    requiredFieldsHeader.hidden = fieldStatus.required.length === 0;
    optionalFieldsHeader.hidden = fieldStatus.optional.length === 0;

    citationFields.forEach((citationField, defaultOrderIndex) => { 
      const fieldId = citationField.id;
      if (fieldStatus.required.includes(fieldId)) {
        citationField.hidden = false;
        citationField.style.order = (100 + defaultOrderIndex);
      } else if (fieldStatus.optional.includes(fieldId)) {
        citationField.hidden = false;
        citationField.style.order = (200 + defaultOrderIndex);
      } else {
        citationField.hidden = true;
      }
    });
  }
}

function main(DATA) {

  const initDisplay = getRoute();

  // If item specified in URL, select tab and open item

  if (initDisplay.itemId) {
    document.getElementById('item-tab').click();
    DATA.currentItemId = initDisplay.itemId;
    // @todo - the same for persons
    if (initDisplay.personId) {
      // ...
    }
  }

  // Citation form (tab 1)

  const updateCitationFieldVisibility = getUpdateCitationFieldVisibilityCallback(DATA.FIELDS_BY_DOC_TYPE);

  const citationForm = new Vue({
    el: '#citation-form',
    data: DATA,
    watch: {
      'citation_data.citation_type_id': updateCitationFieldVisibility
    },
    methods: {
      onSubmitForm: function(x) { 
        // @todo finish this
        console.log({ 
          submitEvent: x, 
          data: JSON.parse(JSON.stringify(this._data))
        })
      }
    },
    mounted: updateCitationFieldVisibility(DATA.citation_data.citation_type_id)
  });

  // Item form (tab 2)
  // @todo finish item form

  // console.log('XXXXXX', DATA, 'XXXXXXXX');

  window.itemForm = new Vue({
    el: '#Items',
    data: DATA,
    computed: {},
    delimiters: ['v{','}v'], // So as not to clash with Django templates
    mounted: () => console.log('MOUNTED', DATA),
    methods: {
      makeNewReferent: function () {
        const currentItem = this.items.find(i => i.id === this.currentItemId)
        currentItem.referents.push({
          id: -1,
          names: [{
            id: -1,
            firstName: '', 
            lastName: '',
            type: 0
          }],
          age: undefined, age_number: undefined,
          gender: undefined,
          tribe: undefined,
          race: undefined,
          transcription: undefined 
        });
      },
      makeNewReferentName: function () {
        const currentItem = this.items.find(i => i.id === this.currentItemId),
              currentReferent = currentItem.referents.find(r => r.id === this.currentReferentId),
              newReferentId = uuidv4();
        currentReferent.names.push({
          id: newReferentId,
          firstName: '', 
          lastName: '',
          type: 0
        });
        this.currentNameId = newReferentId;
      },
      makeNewItem: function () {
        this.items.push(
          {
            id: -1,
            type: undefined,
            volume: undefined,
            page_start: undefined,
            page_end: undefined,
            title: 'New item'
          }
        );
        this.currentItemId = -1;
      }
    }
  });
}

async function loadAndInitializeData(initDisplay) {

  let dataAndSettings = await getSourceData();

  // Set initial item to display:
  //  from URL, assign to first item, or undefined

  dataAndSettings.currentItemId = 
    initDisplay.itemId || 
    Object.keys(dataAndSettings.formData.doc.references)[0] ||
    undefined;

  // Set first referent to display: from URL or none

  dataAndSettings.currentReferentId = initDisplay.referentId || -1;

  // Load full data for current item

  dataAndSettings.formData.doc.references[dataAndSettings.currentItemId] 
    = await getItemData(dataAndSettings.currentItemId);

  // Initialize save status register

  dataAndSettings.saveStatus = 'saved';

  return dataAndSettings;
}

// Main routine

async function main() {

  // Get initial item/referent display selector from URL

  const initDisplay = getRoute();

  // Get the data structure to pass to Vue

  let dataAndSettings = await loadAndInitializeData(initDisplay);
  console.log(dataAndSettings);

  // If item specified in URL, select tab

  if (initDisplay.itemId) {
    document.getElementById('item-tab').click();
  }

  // Initialize forms

  initializeCitationForm(dataAndSettings);
  initializeItemForm(dataAndSettings);
}

main();

/*

  @todo

  Use Tagify (as a Vue component?) on appropriate fields
    https://yaireo.github.io/tagify/
  Create a Vue component for ID badges
  Add relationships between people
  Add GUI editor for transcription (convert to markdown?)

*/

