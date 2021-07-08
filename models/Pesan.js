const { Model } = require('vertex360')({ site_id: process.env.TURBO_APP_ID })

const props = {
  nama: { type: String, default: '', display:true },
  email: { type: String, default: '' },
  pesan: { type: String, default: '' },
  schema: { type: String, default: 'pesan', immutable: true },
  timestamp: { type: Date, default: new Date(), immutable: true }
}

class Pesan extends Model {
  constructor () {
    super()
    this.schema(props)
  }
}

module.exports = Pesan
