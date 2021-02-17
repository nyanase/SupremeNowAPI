const mongoose = require("mongoose")

mongoose.connect('mongodb://localhost:27017/supremeNow', () =>
  console.log('connected to mongo!')
)