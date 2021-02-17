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
  }
})


module.exports = mongoose.model('Case', caseSchema)