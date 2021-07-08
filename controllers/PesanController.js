const { Controller } = require('vertex360')({ site_id: process.env.TURBO_APP_ID })
const Pesan = require('../models/Pesan')

class PesanController extends Controller {
  constructor () {
    super(Pesan, process.env)
  }

  async get (params) {
    const pesans = await Pesan.find(params, Controller.parseFilters(params))
    return Pesan.convertToJson(pesans)
  }

  async getById (id) {
    const pesan = await Pesan.findById(id)
    if (pesan == null) {
      throw new Error(`${Pesan.resourceName} ${id} not found.`)
    }

    return pesan.summary()
  }

  async post (body) {
    const pesan = await Pesan.create(body)
    return pesan.summary()
  }

  async put (id, params) {
    const pesan = await Pesan.findByIdAndUpdate(id, params, { new: true })
    return pesan.summary()
  }

  async delete (id) {
    const pesan = await Pesan.findByIdAndRemove(id)
    return pesan
  }
}

module.exports = new PesanController()

