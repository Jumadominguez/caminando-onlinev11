const userModels = require('./user');
const productModels = require('./product');
const commerceModels = require('./commerce');
const systemModels = require('./system');

module.exports = {
  ...userModels,
  ...productModels,
  ...commerceModels,
  ...systemModels
};