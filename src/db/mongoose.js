// const mongoose = require("mongoose")

mongoose.connect('mongodb://localhost:27017/supremeNow', () =>
  console.log('connected to mongo!')
)

// const mongoose = require('mongoose');
// const connection = "mongodb+srv://nyanase:supremenow-nvma@supremenow-api-cluster.pm20k.mongodb.net/supremeNow?retryWrites=true&w=majority";
// mongoose.connect(connection,{ useNewUrlParser: true, useUnifiedTopology: true, useFindAndModify: false})
//     .then(() => console.log("Database Connected Successfully"))
//     .catch(err => console.log(err));
