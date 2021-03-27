const express = require("express");
const multer = require("multer");
const sharp = require("sharp");
const router = express.Router();
const Article = require("../models/article");

router.get("/", async (req, res) => {
  try {
    const articles = await Article.find();
    res.json(articles);
  } catch (err) {
    res.status(500).json({ message: err });
  }
});

router.get("/docket/:docket", getArticles, async (req, res) => {
  res.json(res.articles);
});

router.post("/content", async (req, res) => {
  const newArticle = new Article(req.body);
  try {
    const savedArticle = await newArticle.save();
    res.status(201).json(savedArticle);
  } catch (err) {
    res.status(400).json({ message: err });
  }
});

const upload = multer({
  limits: { fileSize: 1000000 },
  fileFilter(req, file, cb) {
    if (!file.originalname.match(/\.(png|jpg|jpeg)$/)) {
      return cb(new Error("Please upload an image"));
    }
    cb(undefined, true);
  },
});

router.delete("/all", async (req, res) => {
  try {
    const articles = await Article.deleteMany({});
    res.json(articles);
  } catch (err) {
    res.status(500).json({ message: err });
  }
});

router.delete("/docket/:docket", async (req, res) => {
  try {
    const articles = await Article.deleteMany({ docket: req.params.docket });
    res.json(articles);
  } catch (err) {
    res.status(500).json({ message: err });
  }
});

router.post(
  "/image/:id",
  upload.single("image"),
  async (req, res) => {
    if (!req.file) return res.status(400).send();
    try {
      const article = await Article.findOne({ _id: req.params.id });
      if (!article) return res.status(404).send();
      const buffer = await sharp(req.file.buffer)
        .resize({ width: 275 })
        .png()
        .toBuffer();
      article.image = buffer;
      article.has_image = true;
      await article.save();
      res.send();
    } catch (e) {
      res.status(500).send();
    }
  },
  (error, req, res, next) => {
    res.status(400).send({ error: error.message });
  }
);

router.get("/image/:id", async (req, res) => {
  try {
    const article = await Article.findOne({ _id: req.params.id });
    if (!article || !article.image) throw new Error();
    res.set("Content-Type", "image/png");
    res.send(article.image);
  } catch (e) {
    res.status(404).send();
  }
});

async function getArticles(req, res, next) {
  let articles;
  try {
    articles = await Article.find({ docket: req.params.docket });
    if (articles == null) {
      return res.status(404).json({ message: "Cannot find articles" });
    }
  } catch (err) {
    return res.status(500).json({ message: err });
  }

  res.articles = articles;
  next();
}

// async function getCasesByYear(req, res, next) {
//   let cases
//   try {
//     cases = await Case.find({'year': req.params.year})
//     if (cases == null) {
//       return res.status(404).json({ message: 'Cannot find cases' })
//     }
//   } catch (err) {
//     return res.status(500).json({ message: err })
//   }

//   res.cases = cases
//   next()
// }

// async function getActiveCases(req, res, next) {
//   let cases
//   try {
//     cases = await Case.find({'decided': null})
//     if (cases == null) {
//       return res.status(404).json({ message: 'Cannot find cases' })
//     }
//   } catch (err) {
//     return res.status(500).json({ message: err })
//   }

//   res.cases = cases
//   next()
// }

module.exports = router;
