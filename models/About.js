const { Model } = require('vertex360')({ site_id: process.env.TURBO_APP_ID })

const props = {
  about: { type: String, default: '', isHtml: true },
  schema: { type: String, default: 'about', immutable: true },
  timestamp: { type: Date, default: new Date(), immutable: true }
}

class About extends Model {
  constructor () {
    super()
    this.schema(props)
  }
}

module.exports = About
