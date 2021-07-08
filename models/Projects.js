const { Model } = require('vertex360')({ site_id: process.env.TURBO_APP_ID })

const props = {
  image: { type: String, default: '' },
  judul: { type: String, default: '', display:true },
  deskripsi: { type: String, default: '', isHtml: true },
  schema:{type: String, default:'projects', immutable:true},
  timestamp:{type: Date, default: new Date(), immutable:true}
}

class Projects extends Model {
  constructor () {
    super()
    this.schema(props)
  }
}

module.exports = Projects
