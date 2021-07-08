const { Controller } = require('vertex360')({ site_id: process.env.TURBO_APP_ID })
const Projects = require('../models/Projects')

class ProjectsController extends Controller {
  constructor () {
    super(Projects, process.env)
  }

  async get (params) {
    const projectss = await Projects.find(params, Controller.parseFilters(params))
    return Projects.convertToJson(projectss)
  }

  async getById (id) {
    const projects = await Projects.findById(id)
    if (projects == null) {
      throw new Error(`${Projects.resourceName} ${id} not found.`)
    }

    return projects.summary()
  }

  async post (body) {
    const projects = await Projects.create(body)
    return projects.summary()
  }

  async put (id, params) {
    const projects = await Projects.findByIdAndUpdate(id, params, { new: true })
    return projects.summary()
  }

  async delete (id) {
    const projects = await Projects.findByIdAndRemove(id)
    return projects
  }
}

module.exports = new ProjectsController()

