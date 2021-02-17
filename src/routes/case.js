const express = require('express');
const router = express.Router();
const Case = require('../models/case');

router.post('/', (req, res) => {
  const newCase = new Case({
    name: req.body.name,
    docket: req.body.docket,
    petitioner: req.body.petitioner,
  })

  newCase.save()
    .then(data => {
      res.json(data)
    })
    .catch(err => {
      res.json({ message: err })
    })
});

module.exports = router;