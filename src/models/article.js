const mongoose = require("mongoose");

const articleSchema = new mongoose.Schema({
  source: {
    type: String,
    default: null,
  },
  author: {
    type: String,
    default: null,
  },
  title: {
    type: String,
    default: null,
  },
  content: {
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
  image_url: {
    type: String,
    default: null,
  },
  image: {
    type: Buffer,
  },
  published: {
    type: String,
    default: null,
  },
  docket: {
    type: String,
    required: true,
  },
  name: {
    type: String,
    required: true,
  },
  has_image: {
    type: Boolean,
    default: false,
  },
});

articleSchema.methods.toJSON = function () {
  const article = this;
  const articleObject = article.toObject();
  delete articleObject.image;
  return articleObject;
};

module.exports = mongoose.model("Article", articleSchema);
