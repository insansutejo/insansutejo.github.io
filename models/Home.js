const { Model } = require('vertex360')({ site_id: process.env.TURBO_APP_ID })

const props = {
  image: { type: String, default: '' },
  nama: { type: String, default: '', display:true },
  pekerjaan: { type: String, default: ''},
  schema: { type: String, default: 'home', immutable: true },
  timestamp: { type: Date, default: new Date(), immutable: true }
}

class Home extends Model {
  constructor () {
    super()
    this.schema(props)
  }
}

module.exports = Home
