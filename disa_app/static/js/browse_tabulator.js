
(function() { // Open IIFE

  // Constants

  const DATA_ENDPOINT_URL = document.getElementById('browse_json_url').value,
        NAME_DISPLAY_OVERRIDES = {
          'unrecorded': 'No name is recorded ',
          'Unknown': 'No name is known '
        },
        BIO_THEME_CLASSNAME = 'biographical',
        VIEW_OPTIONS_RADIO_BUTTONS_ID = 'view-options',
        MIN_TIME_BETWEEN_LUNR_INDEXES = 1000,
        ADULT_CHILD_CUTOFF_AGE = 16,
        ENSLAVED_ROLES = [
          'Enslaved',
          'Bought',
          'Sold',
          'Shipped',
          'Arrived',
          'Escaped',
          'Captured',
          'Emancipated'
        ],
        ENSLAVER_ROLES = [
          'Owner',
          'Captor',
          'Buyer',
          'Seller',
          'Master'
        ],
        ENSLAVEMENT_STATUS = {
          ENSLAVED: 'Enslaved',
          ENSLAVER: 'Enslaver',
          DEFAULT: 'Neither or unknown'
        },
        MAX_NUMBER_OF_ENTRIES = 100000,
        REF_COUNT_ELEM_ID = 'ref-count',
        ITEM_COUNT_ELEM_ID = 'item-count';

  // Event handlers

  window.disa = {};

  window.populateTribeFilter = function(tribeName) {
    window.table.setHeaderFilterValue('all_tribes', tribeName);
  }

  window.populateNameFilter = function(nameSearchText) {
    window.table.setHeaderFilterValue('all_name', nameSearchText);
  }

  window.populateLocationFilter = function(locationSearchText) {
    window.table.setHeaderFilterValue('reference_data.all_locations', locationSearchText);
  }

  // Called when "details" button pressed

  let detailsModal;

  window.showDetails = function(id) {

    const data = window.disa.jsonData.find(x => x.referent_db_id === id);

    // Initialize modal (only done once)

    function getModalContentSetter(idOrClass, textOrHTML) {
      const elems = document.querySelectorAll(`#${idOrClass},.${idOrClass}`);
      return function(content) {
        elems.forEach(elem => elem[`inner${textOrHTML}`] = content);
      }
    }

    const setDetailsTable = getModalContentSetter('details-table', 'HTML'),
          setDocDetailsTable = getModalContentSetter('source-details-table', 'HTML');

    if (detailsModal === undefined) {
      detailsModal = {
        show: () => $('#details-modal').modal('show'),
        setId: getModalContentSetter('details-id', 'Text'),
        setName: getModalContentSetter('details-title-name', 'Text'),
        setDocTitle: getModalContentSetter('details-doc', 'Text'),
        setTranscription: getModalContentSetter('details-transcription', 'HTML'),
        setItemImageLink: imgUrl => document.getElementById('item-facsimile').setAttribute('href', imgUrl || ''),
        clearDetailsTable: () => setDetailsTable(''),
        addToDetailsTable: (label, value) => {
          document.getElementById('details-table').innerHTML +=
            `<tr><th>${label}</th><td>${value}</td></tr>`;
        },
        clearDocDetailsTable: () => setDocDetailsTable(''),
        addToDocDetailsTable: (label, value) => {
          document.getElementById('source-details-table').innerHTML +=
            `<tr><th>${label}</th><td>${value}</td></tr>`;
        }
      }
    }

    // Populate modal

    if (data) {

      detailsModal.setName(data.all_name);
      detailsModal.setId(id);
      // detailsModal.transcription(data.comments.replace(/http[^\s]+/,''));
      detailsModal.setTranscription(data.reference_data.transcription);
      detailsModal.setItemImageLink(data.reference_data.image_url);
      detailsModal.setDocTitle(uncleanString(data.citation_data.display.replace(/http[^\s]+/,'')));
      detailsModal.clearDetailsTable();
      detailsModal.clearDocDetailsTable();

      // Load referent data into details table

      const detailsTableContent = [
        ['Location', data.reference_data.all_locations],
        ['First name', data.name_first],
        ['Last name', data.name_last],
        ['Role(s)', data.all_roles],
        // ['Date', new Date(data.date.year, data.date.month, data.date.day).toDateString()],
        ['Tribe', data.all_tribes],
        ['Sex', data.sex],
        ['Origin', data.all_origins],
        ['Vocation', data.vocations.join(', ')],
        ['Age', data.age]
      ];

      // Load relationships into details table

      data.relationships.forEach(r => {
        detailsTableContent.push([
          r.description.charAt(0).toUpperCase() + r.description.slice(1),
          [ r.related_referent_info.related_referent_first_name,
            r.related_referent_info.related_referent_last_name
          ].join(' ') + `&nbsp;<div class="badge badge-primary">id <span id="details-id">${r.related_referent_info.related_referent_db_id}</span></div>`
        ])
      });

      detailsTableContent.filter(x => x[1])
        .forEach(([label, value]) => detailsModal.addToDetailsTable(label, value));

      // Load document details into a table

      const docDetailsTable = [
        ['Item type', data.reference_data.reference_type],
        ['Item ID', `<span class="badge badge-primary">${data.reference_data.reference_db_id}</span>`],
        ['Item date', data.reference_data.date_display],
        ['Location of event described in the item', data.reference_data.all_locations],
        ['National context of item', data.reference_data.national_context],
        ['Item appears in document with title', `<cite>${ uncleanString(data.citation_data.display)}</cite>`],
        ['Document type', data.citation_data.citation_type],
        ['Document ID', `<span class="badge badge-primary">${data.citation_data.citation_db_id}`]
      ];

      docDetailsTable.filter(x => x[1])
        .forEach(([label, value]) => detailsModal.addToDocDetailsTable(label, value));

      detailsModal.show();
    }
  }

  // Global functions

  // Toggle special characters (single/double quotes; ampersand)
  //  with special codes
  // WARNING: don't use with transcription

  const ampersandRegex = /&(?!\w+;)/,
        aposRegEx = /'/g,
        quotRegEx = /"/g,
        aposRegEx_reverse = /\[APOS]/g,
        quotRegEx_reverse = /\[QUOT]/g,
        ampersandRegex_reverse = /\[AMP]/g,
        inlineCssRegex = /\s+style="[^"]*"/g;

  function cleanString(str) {
    if (typeof str !== 'string') {
      return '';
    } else {
      return str.replace(aposRegEx, '[APOS]')
      .replace(quotRegEx, '[QUOT]')
      .replace(ampersandRegex, '[AMP]')
      .replace(inlineCssRegex,'');
    }
  }

  function uncleanString(str) {
    return str.replace(aposRegEx_reverse, "'")
              .replace(quotRegEx_reverse, '"')
              .replace(ampersandRegex_reverse, '&amp;');
  }

  // Lunr index function

  let lunrIndex, currLunrSelection;

  function indexInLunr(data) {

    // Create a list of documents with ID
    //   and text (which combines all the DISA fields to search)

    const docList = data.map(entry => {

      const indexableText = [
        entry.all_name,
        entry.reference_data.all_locations,
        entry.citation_data.display,
        entry.reference_data.transcription,
        entry.enslavement_status
      ].join(' ');

      const indexableText_noHTML = indexableText.replace(/\<[^>]+>/g, '');

      return {
        id: entry.referent_db_id,
        text: indexableText_noHTML
      }
    });

    // Create lunr index from the documents

    const index = lunr( function () {
      this.ref('id');
      this.field('text');

      docList.forEach(function (document) {
        this.add(document)
      }, this);
    });

    return index;
  }

  // Main onload routine

  window.addEventListener('DOMContentLoaded', () => {

    // General search box listener
    //   When user inputs something, trigger a re-indexing

    document.getElementById('general-search')
            .addEventListener('input', searchAgainstIndex);

    // Run the JSON through this when it comes back from the
    //  server. Save the data.

    const jsonProcessor = function(_, __, response) {

      console.log('JSON response', response);

      // Update count stats

      document.getElementById(REF_COUNT_ELEM_ID).innerText = response.meta.referents_count;
      document.getElementById(ITEM_COUNT_ELEM_ID).innerText = response.referent_list.reduce(
        (setOfRefs, currRef) => setOfRefs.add(currRef.reference_data.reference_db_id),
        new Set()
      ).size;

      // Create an 'all_names' field
      // Create an 'all_locations' field
      // Clean up data for apostrophes, ampersands

      let processedResponse = response.referent_list.map(entry => {

        // Copy all properties over to newEntry

        let newEntry = JSON.parse(JSON.stringify(entry));

        // Clean strings

        newEntry.name_first = cleanString(newEntry.name_first);
        newEntry.name_last = cleanString(newEntry.name_last);
        newEntry.tribes = newEntry.tribes.map(cleanString);
        newEntry.citation_data.display = cleanString(newEntry.citation_data.display);
        newEntry.citation_data.comments = cleanString(newEntry.citation_data.comments);
        // newEntry.reference_data.transcription = cleanString(newEntry.reference_data.transcription);
        newEntry.reference_data.locations.forEach(
          loc => loc.location_name = cleanString(loc.location_name)
        );
        newEntry.sex = newEntry.sex === '(not-recorded)' ? '' : newEntry.sex;

        // Additional tabulator/lunr fields

        newEntry.all_name = [newEntry.name_first, newEntry.name_last]
          .filter(name => (name))
          .join(' ');

        newEntry.all_tribes = newEntry.tribes.join(', ');

        newEntry.reference_data.all_locations = newEntry.reference_data.locations
          .reverse()
          .map(loc => loc.location_name)
          .join(', ');

        newEntry.all_roles = newEntry.roles.join(', ');

        function includesAny(compareArr1, compareArr2) {
          return compareArr1.reduce(
            (acc, role) => acc || compareArr2.includes(role),
            false
          )
        }

        if (includesAny(entry.roles, ENSLAVED_ROLES)) {
          newEntry.enslavement_status = ENSLAVEMENT_STATUS.ENSLAVED;
        } else if (includesAny(entry.roles, ENSLAVER_ROLES)) {
          newEntry.enslavement_status = ENSLAVEMENT_STATUS.ENSLAVER;
        } else {
          newEntry.enslavement_status = ENSLAVEMENT_STATUS.DEFAULT;
        }

        newEntry.all_origins = newEntry.origins.join(', ');
        newEntry.all_tribes = newEntry.tribes.join(', ');
        newEntry.all_races = newEntry.races.join(', ');
        newEntry.year = (new Date(entry.reference_data.date_db)).getFullYear();

        // Some additional fields for Maiah's download

        newEntry.vocation = newEntry.vocations.join(',');

        newEntry.enslaved_by = newEntry.relationships.filter(
          rel => (rel.description === 'enslaved by')
        ).map(
          rel => rel.related_referent_info.related_referent_first_name + ' ' +
                 rel.related_referent_info.related_referent_last_name
        ).join('; ');

        newEntry.enslaved = newEntry.relationships.filter(
          rel => (rel.description === 'owner of')
        ).map(
          rel => rel.related_referent_info.related_referent_first_name + ' ' +
                  rel.related_referent_info.related_referent_last_name
        ).join('; ');

        return newEntry;
      });

      console.log('JSON after processing', processedResponse);

      // Index this in Lunr

      lunrIndex = indexInLunr(processedResponse);
      window.disa.lunrIndex = lunrIndex; // For testing
      searchAgainstIndex(); // Initialize results array for general search

      // Save this data for later

      window.disa.jsonData = processedResponse;

      // Return data to Tabulator

      return processedResponse;
    }

    // Given an entry, create a biographical sketch in HTML

    const getPersonEntryHTML = function(entry) {

      const nameDisplay = NAME_DISPLAY_OVERRIDES[entry.name_first] || entry.name_first,
            name_text = // entry.description.title
                        `<a href="#" onclick="populateNameFilter('${nameDisplay}')" title="Show only people named '${nameDisplay}'">${uncleanString(nameDisplay)}</a>`
                        + (entry.name_last ? ` <a href="#" onclick="populateNameFilter('${entry.name_last}')" title="Show only people with last name '${entry.name_last}'">${uncleanString(entry.name_last)}</a>` : ''),
            name_forOrIs = NAME_DISPLAY_OVERRIDES[entry.name_first] ? 'for' : 'is',
            statusDisplay = { // @todo make a global constant?
              [ENSLAVEMENT_STATUS.ENSLAVED]: 'enslaved',
              [ENSLAVEMENT_STATUS.ENSLAVER]: 'slave-owning',
              [ENSLAVEMENT_STATUS.DEFAULT]: ''
            },
            locSearchTerms = entry.reference_data.locations.map(
              (_, i, locArr) => locArr.slice(i).map(x => x.location_name).join(', ')
            ),
            locationDisplay = entry.reference_data.locations.map((loc, i) => {
              return `<a  href="#" onclick="populateLocationFilter('${locSearchTerms[i]}')"
                          title="Show only people located in ${locSearchTerms[i]}">${uncleanString(loc.location_name)}</a>`
            }).join(', '),
            sexDisplay = { // @todo make a global constant?
              'child': {
                'Female' : 'girl',
                'Male': 'boy',
                'Other': 'child',
                '': 'child'
              },
              'adult': {
                'Female': 'woman',
                'Male': 'man',
                'Other': 'individual',
                '': 'individual'
              },
              'pronoun': {
                'Female': { cap: 'She', nocap: 'she', be_conj: 'was'},
                'Male': { cap: 'He', nocap: 'he', be_conj: 'was'},
                'Other': { cap: 'They', nocap: 'they', be_conj: 'were'},
                '': { cap: 'They', nocap: 'they', be_conj: 'were'}
              }
            },
            ageAsNumber = parseInt(entry.age.replaceAll(/[^\d]/g, '')),
            age_number = (isNaN(ageAsNumber) ? undefined : ageAsNumber),
            ageStatus = (age_number && age_number <= ADULT_CHILD_CUTOFF_AGE ? 'child' : 'adult'),
            age_text = (entry.age === '(not-recorded)' ? undefined : entry.age),
            race_text = (entry.all_races ? `, described as &ldquo;${entry.all_races}&rdquo;,` : ''),
            year = entry.year,
            proNounCap = sexDisplay.pronoun[entry.sex].cap,
            toBe_conj = sexDisplay.pronoun[entry.sex].be_conj;

      // GENERATE RELATIONSHIPS DESCRIPTION
      
      const relationshipsArrayHTML = entry.relationships.map(relationship => {
        let html;
        const relRefInfo = relationship.related_referent_info,
              relRefName = [relRefInfo.related_referent_first_name, relRefInfo.related_referent_last_name]
                            .filter(x => x.length)
                            .join(' '),
              relRefNameLink = `<a href='#' onclick='showDetails(${relRefInfo.related_referent_db_id})' 
                                   title='Details about ${relRefName}'>${relRefName}</a>`;
        if (relationship.description === 'enslaved by') {
          html = `${toBe_conj} enslaved by ${relRefNameLink}`;
        } else if (relationship.description === 'owner of') {
          html = `enslaved ${relRefNameLink}`;
        } else if (relationship.description === 'escaped from') {
          html = `escaped from ${relRefNameLink}`;
        } else if (relationship.description === 'sold by') {
          html = `${toBe_conj} sold by ${relRefNameLink}`;
        } else if (relationship.description === 'mother of' || relationship.description === 'father of') {
          html = `had a child, ${relRefNameLink}`;
        } else if (relationship.description === 'child of') {
          html = `${toBe_conj} the child of ${relRefNameLink}`;
        } else {
          html = undefined;
        }
        return html;
      }).filter(r => r !== undefined);

      let relationshipsHTML;

      if (relationshipsArrayHTML.length) {
        const lastRel = relationshipsArrayHTML.pop();
        relationshipsHTML = ' ' + proNounCap + ' ' +
                            (relationshipsArrayHTML.length 
                              ? `${relationshipsArrayHTML.join(', ')}, and ` 
                              : '') +
                            lastRel + '.';
      } else {
        relationshipsHTML = ''
      }
      
      // COMPILE FINAL HTML

      const html = `<a  class="details-button float-right" onclick="showDetails(${entry.referent_db_id})"
                        title="Show source document and details for ${entry.all_name}">Details</a>` +
                   `<strong class='referent-name'>${name_text}</strong> ${name_forOrIs} ` +
                   (statusDisplay[entry.enslavement_status][0] === 'e' ? 'an ' : 'a ') +
                   statusDisplay[entry.enslavement_status] + ' ' +
                   // (entry.description.tribe ? ` <a href="#" title="Show only ${entry.description.tribe} people" data-filter-function='populateTribeFilter' data-filter-arg="${entry.description.tribe}" onclick="populateTribeFilter('${entry.description.tribe}')">${entry.description.tribe}</a> ` : '') +
                   (entry.tribes[0] ? ` <a href="#" title="Show only ${entry.tribes[0]} people" data-filter-function='populateTribeFilter' data-filter-arg="${entry.tribes[0]}">${entry.tribes[0]}</a> ` : '') +
                   sexDisplay[ageStatus][entry.sex] +
                   // `:: ${ageStatus}  / ${entry.sex} ::` +
                   (age_text ? `, age ${age_text}` : '') +
                   race_text +
                   ' who lived' +
                   ` in ${locationDisplay}` +
                   (year ? ` in ${year}` : '') +
                   '.' + 
                   relationshipsHTML;

      return html;
    }

    const rowFormatter = function(row) {
      var entry = row.getData();
      row.getElement().innerHTML = getPersonEntryHTML(entry);
    };

    // Clean the cruft (mostly MSOffice markup) out of the transcription
    //  before download

    const transcriptionDownloadAccessor = function(value) {
      const noStyle = value.replace(/<style>.*<\/style>/gis, ''),
            noMSOfficeGarbage = noStyle.replace(/<([wmo]:\w+)[^>]*>.*?<\/\1[^>]*>/gis, ''),
            noHTML = noMSOfficeGarbage.replace(/<[^>]+>/g, ''),
            cleanSpaces = noHTML.replace(/(\s\s+|\n)/gs, ' ');
      return cleanSpaces;
    }

    const generateDropDownOptions = function(data, selectorFn) {
      const values = data.map(x => selectorFn(x)),
            uniqueValues = Array.from(new Set(values));
      return uniqueValues.keys();
    }

    const columnDefinitions = [

      { title:'Name',      field:'all_name',          sorter:'string', headerFilter: true }, // mutator: combineNames_mutator },
      { title:'Last name', field:'name_last',         sorter:'string', headerFilter: true, visible: false },
      { title:'Status',    field:'enslavement_status',            sorter:'string', headerFilter: true,
        headerFilter: 'select', headerFilterParams:{ values: ['Enslaved','Enslaver','Neither'] }, download: true },
      // { title:'Roles',    field:'roles',              sorter:'string', headerFilter: true },
      { title:'Sex',       field:'sex',   sorter:'string',
        headerFilter: 'select', headerFilterParams:{ values: ['Male','Female', 'Other'] } },
      { title:'Tribe',     field:'all_tribes', sorter:'string',
        headerFilter: 'select',
        headerFilterParams: {
          values: [ '"daughter of a Spanish Squaw"', "Apalachee", "Blanco", "Blanea", "Bocotora",
                    "Bousora", "Boustora", "Chaliba", "Cherokee", "Codira", "Cookra", "Creek",
                    "Cuol", "Curero", "Eastern Pequot", "Eastern Tribes", "Mashantucket Pequot",
                    "Mohegan", "Naragansett", "Natchez", "Nidwa", "Nipmuc", "Noleva", "Nome Lackee",
                    "Nomi Lackee", "Oquelonex", "Pequot", "Portoback", "Rocotora", "Sambo", "Shaliba",
                    "Shalliba", "Shangina", "Shargana", "Shatyana", "Souix,Sioux", "Spanish", "Talusky",
                    "Tanybec", "Tenebec", "Tenybec", "Terriby", "Thalliba", "Toluskey", "Unspecified",
                    "Valiante", "Valience", "Wackaway", "Wampanoag", "Warao", "Weanoke,Weanock,Powhatan",
                    "Weyanoke", "Woolwa", "de Nacion Caribe Cuchibero" ]
        }
      },
      { title:'Race',      field:'all_races',  sorter:'string',
        headerFilter: 'select',
        headerFilterParams: {
          values: [ "Asiatic", "Black", "Carolina Indian", "Creole", "Creole", "Dark melattress",
                    "Dark mulatto", "East India Negro", "East-India Indian", "East-Indian", "Griffon",
                    "Half Indian", "Half Indian", "Half Negro", "Indian", "Indian Mulatto", "Irish",
                    "Martha's Vineyard Indian", "Mulatto", "Mustee", "Negro", "Sambo", "Spanish Indian",
                    "Surinam Indian", "White" ]
        }
      },
      // { title:'Age',       field:'description.age',   sorter:'string', headerFilter: true },
      { title:'Location',  field:'reference_data.all_locations',     sorter:'string', headerFilter: true },
      { title:'Year',      field:'year',         sorter:'string', headerFilter: true },

      // Some hidden fields just for downloading and general search

      { title:'Source transcription', field:'reference_data.transcription', visible: false, download: true, accessorDownload:transcriptionDownloadAccessor },
      { title:'Referent_ID', field:'referent_db_id', visible: false, download: true },
      { title:'Vocation', field:'vocation', visible: false, download: true },
      { title:'Age', field:'age', visible: false, download: true },
      { title:'Reference_ID', field:'reference_data.reference_db_id', visible: false, download: true },
      { title:'Enslaved_by', field:'enslaved_by', visible: false, download: true },
      { title:'Enslaved', field:'enslaved', visible: false, download: true }
    ];

    const rowClick = function(_, row) {
      showDetails(row.getData().referent_db_id);
    };

    const doFilter = function(e) {
      const funcName = e.target.getAttribute('data-filter-function'),
            funcArg = e.target.getAttribute('data-filter-arg');

    }

    const tabulatorOptions_global = {
      height:'611px',
      layout:'fitColumns',
      placeholder:'No records match these criteria<br />Try removing filters to broaden your search',
      pagination: 'local',
      paginationSize: 20,
      paginationSizeSelector:[20,50,100,10000],
      columns: columnDefinitions,
      downloadRowRange: 'active',
      renderComplete: () => {
        console.log('RENDER COMPLETE');
        document.querySelectorAll("*[data-filter-function]").forEach(
          x => {
            // const onclickFunction = () => window[x.getAttribute('data-filter-function')](x.getAttribute('data-filter-arg'));
            const onclickFunctionName = x.getAttribute('data-filter-function'),
                  onclickFunctionArg = x.getAttribute('data-filter-arg'),
                  onclickFunction = () => window[onclickFunctionName](onclickFunctionArg);
            x.addEventListener('click', onclickFunction, true);
          }
        )
      }
      //groupBy:'status'
    }

    const tabulatorOptions_init = Object.assign(
      [],
      tabulatorOptions_global,
      {
        ajaxURL: DATA_ENDPOINT_URL,
        ajaxResponse: jsonProcessor,
        rowFormatter: rowFormatter
      }
    );

    let table = new Tabulator('#data-display', tabulatorOptions_init);

    table.addFilter(data => {
      return currLunrSelection.includes(data.referent_db_id);
    });

    // Listener for the biographical/tabular view selector

    const bioViewOptionInputElem = document.getElementById('biographical-view-option'),
          tableContainer = document.getElementById('data-display');

    document.getElementById(VIEW_OPTIONS_RADIO_BUTTONS_ID).addEventListener('click', () => {

      const bioOption = bioViewOptionInputElem.checked;

      const tabulatorOptions_view = bioOption
        ? { rowFormatter }
        : { rowClick };

      const tabulatorOptions_dataLoaded = {
        data: window.disa.jsonData
      }

      table.destroy();
      tableContainer.classList.toggle(BIO_THEME_CLASSNAME, bioOption);

      table = new Tabulator(
        '#data-display',
        Object.assign({},
          tabulatorOptions_global,
          tabulatorOptions_dataLoaded,
          tabulatorOptions_view
        )
      );

      table.addFilter(data => {
        return currLunrSelection.includes(data.referent_db_id);
      });

      window.table = table;
    });

    window.table = table;

    document.getElementById('download-data')
            .addEventListener('click', () => {
              const oldPageSize = window.table.getPageSize();
              window.table.setPageSize(MAX_NUMBER_OF_ENTRIES);
              window.table.download('csv', `disa-data-export_${Date.now()}.csv`);
              window.table.setPageSize(oldPageSize);
            });

    // This is called every time a user changes the content of the
    //   general search box

    let lastSearchTimestamp = 0, timeOutId;
    const generalSearchInput = document.getElementById('general-search');

    function searchAgainstIndex(x) {

      const searchTextChanged = (x !== false);

      // If enough time has passed ...

      if (Date.now() - lastSearchTimestamp > MIN_TIME_BETWEEN_LUNR_INDEXES) {

        // Do a search against index & force Tabulator to reapply filters

        currLunrSelection = lunrIndex.search(generalSearchInput.value).map(x => parseInt(x.ref));
        console.log(`Searching for ${generalSearchInput.value}`, 'Results:', currLunrSelection);
        table.setFilter(table.getFilters());

        // Update times

        lastSearchTimestamp = Date.now();

        // If this update is becuase of a change in the
        //   search field, then schedule a future
        //   search to catch any changes

        if (searchTextChanged) {
          window.clearTimeout(timeOutId);
          timeOutId = window.setTimeout(
            () => { searchAgainstIndex(false) },
            MIN_TIME_BETWEEN_LUNR_INDEXES + 100
          );
        }
      }
    }
  });

})() // Close IIFE


/* DATA STRUCTURE FOR REFERENCE

{
  "referent_db_id": 317,
  "referent_uuid": "(not-recorded)",
  "name_first": "Nelly",
  "name_last": "",
  "tribes": ['abc'],
  "all_tribes": "abc",
  "sex": "Female",
  "origins": [],
  "vocations": [],
  "age": "13",
  "races": ["Indian"],
  "all_races": "Indian",
  "roles": [
    "Enslaved"
  ],
  "titles": [],
  "statuses": [
    "Slave"
  ],
  "citation_data": {
    "citation_db_id": 97,
    "citation_uuid": "(not-recorded)",
    "citation_type": "Document",
    "display": "“Return of the Registry of Indians on the Mosquito Shore in the year 1777.” TNA, CO 123/31/123-132.",
    "comments": ""
  },
  "reference_data": {
    "reference_db_id": 146,
    "reference_uuid": "(not-recorded)",
    "reference_type": "Inventory",
    "national_context": "British",
    "date_db": "1777-02-26 00:00:00",
    "date_display": "1777 February 26",
    "transcription": "[QUOT]At the Corn Islands at Cape Gracias a Dios at Black River[QUOT]; Same owner as Hemimo, Loraina, [AMP] Alinaes",
    "locations": [
      {
        "location_name": "Mosquito Coast",
        "location_type": null
      },
      {
        "location_name": "British Honduras",
        "location_type": "Colony/State"
      }
    ],
    "all_locations": "Mosquito Coast, British Honduras"
  },
  "relationships": [
    {
      "description": "enslaved by",
      "related_referent_info": {
        "related_referent_db_id": 318,
        "related_referent_first_name": "Robert",
        "related_referent_last_name": "Hodgson"
      }
    }
  ],
  "all_name": "Nelly",
  "all_roles": "Enslaved",
  "enslavement_status": "Enslaved",
  "all_origins": "",
  "year": 1777
}

*/

