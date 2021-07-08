const express = require('express')
const { projects } = require('../controllers')
const { about } = require('../controllers')
const router = express.Router()
const controllers = require('../controllers')

router.get('/',async(req,res,next)=>{
    const data=req.context
    //projects
    const projectsCtr=controllers.projects.instance()
    data.projects = await projectsCtr.get()
    //about
    const aboutCtr=controllers.about.instance()
    data.about= await aboutCtr.get()
    //home
    const homeCtr=controllers.home.instance()
    data.home= await homeCtr.get()

    res.render('home',data)
})

router.get('/projects', async (req,res,next)=>{
    const projectsCtr=controllers.projects.instance()
    const projects= await projectsCtr.get()
    res.json({
        projects
    })
})

router.get('/about', async (req,res,next)=>{
    const aboutCtr=controllers.about.instance()
    const about= await aboutCtr.get()
    res.json({
        about
    })
})

router.get('/home', async (req,res,next)=>{
    const homeCtr=controllers.home.instance()
    const home= await homeCtr.get()
    res.json({
        home
    })
})

router.post('/pesan',async(req,res,next)=>{
    const pesanData = req.body
    const pesanCtr=controllers.pesan.instance()
    const pesan= await pesanCtr.post(pesanData)

    res.json(pesan)
})

module.exports = router 