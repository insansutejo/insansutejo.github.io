const { Controller } = require('vertex360')({ site_id: process.env.TURBO_APP_ID })
const About = require('../models/About')

class AboutController extends Controller {
  constructor () {
    super(About, process.env)
  }

  async get (params) {
    const abouts = await About.find(params, Controller.parseFilters(params))
    return About.convertToJson(abouts)
  }

  async getById (id) {
    const about = await About.findById(id)
    if (about == null) {
      throw new Error(`${About.resourceName} ${id} not found.`)
    }

    return about.summary()
  }

  async post (body) {
    const about = await About.create(body)
    return about.summary()
  }

  async put (id, params) {
    const about = await About.findByIdAndUpdate(id, params, { new: true })
    return about.summary()
  }

  async delete (id) {
    const about = await About.findByIdAndRemove(id)
    return about
  }
}

module.exports = new AboutController()

