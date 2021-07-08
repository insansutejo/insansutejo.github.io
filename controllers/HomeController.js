const { Controller } = require('vertex360')({ site_id: process.env.TURBO_APP_ID })
const Home = require('../models/Home')

class HomeController extends Controller {
  constructor () {
    super(Home, process.env)
  }

  async get (params) {
    const homes = await Home.find(params, Controller.parseFilters(params))
    return Home.convertToJson(homes)
  }

  async getById (id) {
    const home = await Home.findById(id)
    if (home == null) {
      throw new Error(`${Home.resourceName} ${id} not found.`)
    }

    return home.summary()
  }

  async post (body) {
    const home = await Home.create(body)
    return home.summary()
  }

  async put (id, params) {
    const home = await Home.findByIdAndUpdate(id, params, { new: true })
    return home.summary()
  }

  async delete (id) {
    const home = await Home.findByIdAndRemove(id)
    return home
  }
}

module.exports = new HomeController()

