const mongoose = require('mongoose')

const articleSchema = new mongoose.Schema({
  source: {
    type: String,
    default: null,
  },
  author: {
    type: String,
    required: true,
  },
  title: {
    type: String,
    default: null,
  },
  description: {
    type: String,
    default: null,
  },
  url: {
    type: String,
    required: true,
  },
  image: {
    type: Buffer,
  },
  published: {
    type: String,
    default: null
  },
  docket: {
    type: String,
    required: true
  }
})

articleSchema.methods.toJSON = function () {
  const article = this;
  const articleObject = article.toObject();
  delete articleObject.image;
  return articleObject;
};

module.exports = mongoose.model('Article', articleSchema)