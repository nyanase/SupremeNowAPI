const express = require('express')
const mongoose = require("mongoose")
const bodyParser = require('body-parser')
require('dotenv/config')

const casesRoute = require('./routes/case');


const app = express();

app.use(bodyParser.json())

app.use('/cases', casesRoute);

app.get('/', (req, res) => {
  res.send('We are on home');
})


mongoose.connect(
  process.env.DB_CONNECTION,
  { useNewUrlParser: true },
  () => console.log('connected to mongo!')
)

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log('Server running on port', port);
});
