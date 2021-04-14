
import {LOCAL_SETTINGS} from '/static/js/redesign_settings.js';



function preprocessCitationData(data) { 

/*
  // Convert dates to YYYY-MM-DD format
  // @todo should be done on server

  if (data.citation_type_fields.date) {
    data.citation_type_fields.date = 
      (new Date(data.citation_type_fields.date))
      .toISOString()
      .slice(0,10);
  }

  if (data.citation_type_fields.accessDate) {
    data.citation_type_fields.accessDate = 
      (new Date(data.citation_type_fields.accessDate))
      .toISOString()
      .slice(0,10);
  }
  */

  // Convert array of references to hash of references (by ID)

  data.formData.doc.references = data.formData.doc.references.reduce(
    (refObj, ref) => { refObj[ref.id] = ref; return refObj },
    {}
  );

  // Add registers for Vue implementation

  data.currentItemId     = -1;
  data.currentReferentId = -1;
  data.currentNameId     = -1;

  return data;
}

async function getSourceData() {

  const dataURL = new URL(window.location.toString());

  dataURL.hash = '';
  dataURL.search = '?format=json';

  const response = await fetch(dataURL.href),
        dataJSON = await response.json(),
        dataWithSettings = Object.assign({}, LOCAL_SETTINGS, { formData: dataJSON });
  return preprocessCitationData(dataWithSettings);
}

function preprocessItemData(itemData) {
  let processedData = {
    date: itemData.rec.date,
    id: itemData.rec.id,
    location_info: [ // @todo figure this out
      {
        "location_name": "Plymouth",
        "location_type": "Colony/State"
      }
    ],
    national_context_id: itemData.rec.national_context,
    reference_type_id: itemData.rec.record_type.id,
    // reference_type_name: itemData.rec.record_type.label,
    // Convert array of referents to a hash by referent ID
    referents: itemData.entrants.reduce(
      (referentHash, referent) => { referentHash[referent.id] = referent; return referentHash }, 
      {}
    ),
    // referents: getAdditionalReferentInfo(itemData.entrants),
    groups: itemData.groups.group_data,
    transcription: itemData.rec.transcription,
    image_url: itemData.rec.image_url,
    FULL_DATA_LOADED: true // Flag
  }
  return processedData;
}

/*
async function getAdditionalReferentInfo(referents) {
  const referentIDs = referents.map(r => r.id);
} */

async function getItemData(itemId) {
  if (itemId) {
    const dataURL = `/data/records/${itemId}/`,
    response = await fetch(dataURL),
    dataJSON = await response.json();
    return preprocessItemData(dataJSON);
  } else {
    return undefined
  }
}

function preprocessReferentData(referentData) {
  referentData.FULL_DATA_LOADED = true;
  return referentData;
}

async function getReferentData(referentId) {
  if (referentId) {
    const dataURL = `/data/entrants/${referentId}/`,
    response = await fetch(dataURL); // @todo need to handle 404s etc.
    dataJSON = await response.json();

    return preprocessReferentData(dataJSON.ent);
  } else {
    return undefined;
  }
}

export { getSourceData, getItemData, getReferentData }