const mongoose = require('mongoose')

const caseSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
  },
  docket: {
    type: String,
    required: true,
  },
  petitioner: {
    type: String,
    required: true,
  },
  respondent: {
    type: String,
    required: true,
  },
  decided_by: {
    type: String,
    default: null
  },
  lower_court: {
    type: String,
    default: null,
  },
  citation: {
    type: String,
    default: null,
  },
  granted: {
    type: Date,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
  facts: {
    type: String,
    required: true,
  },
  question: {
    type: String,
    required: true,
  },
  argued: {
    type: Date,
    default: null,
  },
  decided: {
    type: Date,
    default: null
  }
})


module.exports = mongoose.model('Case', caseSchema)