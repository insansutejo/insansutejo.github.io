const PostController = require('./PostController')
const ProjectsController = require('./ProjectsController')
const AboutController = require('./AboutController')
const HomeController = require('./HomeController')
const PesanController = require('./PesanController')

module.exports = {
  post: PostController,
  projects:ProjectsController,
  about:AboutController,
  home:HomeController,
  pesan:PesanController
}
