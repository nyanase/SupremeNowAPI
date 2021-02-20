const express = require('express');
const bodyParser = require('body-parser');
require('./db/mongoose');
require('dotenv/config');

const casesRoutes = require('./routes/case');


const app = express();

app.use(bodyParser.json())

app.use('/cases', casesRoutes);

app.get('/', (req, res) => {
  res.send('We are on home');
})


const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log('Server running on port', port);
});
