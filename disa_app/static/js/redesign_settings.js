
export const LOCAL_SETTINGS = {

    AGE_BY_NUMBER_CHECKBOX_ID: "formInputSpecifiedByNumber",
    AGE_BY_NUMBER_DISPLAY_CSS_CLASS: "age-as-number",
    DOC_TYPE_ELEM_ID: "document_type",

    // Data structure for showing / hiding citation fields

    FIELDS_BY_DOC_TYPE: {
      // Book
      20: {
        required: ["author", "date", "pages", "place", "title"],
        optional: [
          "abstractNote",
          "edition",
          "language",
          "series",
          "seriesNumber",
          "shortTitle",
          "url",
        ],
      },
      // Book Section
      21: {
        required: ["author", "date", "pages", "place", "title"],
        optional: [
          "abstractNote",
          "edition",
          "language",
          "section",
          "series",
          "seriesNumber",
          "shortTitle",
          "url",
        ],
      },
      // Document
      26: {
        required: ["author", "date", "pages", "place", "title"],
        optional: ["abstractNote", "archive", "archiveLocation", "language", "url"],
      },
      // Interview
      33: {
        required: ["author", "date", "place", "rights", "title"],
        optional: ["abstractNote", "archive", "archiveLocation", "language", "url"],
      },
      // Journal Article
      34: {
        required: ["author", "date", "pages", "title"],
        optional: ["abstractNote", "language", "url"],
      },
      // Magazine Article
      36: {
        required: ["author", "date", "pages", "title"],
        optional: ["abstractNote", "language", "url"],
      },
      // Manuscript
      37: {
        required: [
          "archive",
          "archiveLocation",
          "author",
          "date",
          "pages",
          "title",
        ],
        optional: ["abstractNote", "language", "place", "url"],
      },
      // Newspaper Article
      39: {
        required: ["date", "edition", "place", "title"],
        optional: [
          "abstractNote",
          "archive",
          "archiveLocation",
          "author",
          "language",
          "pages",
          "section",
          "url",
        ],
      },
      // Thesis
      46: {
        required: ["author", "date", "rights", "title"],
        optional: ["abstractNote", "archive", "archiveLocation", "language", "url"],
      },
      // Webpage
      49: {
        required: ["accessDate", "date", "title", "url"],
        optional: ["author", "language"],
      }
    }
  };
  