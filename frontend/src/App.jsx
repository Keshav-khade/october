import React from 'react'
import './index.css'
import {Route, Routes} from 'react-router-dom'
import Home from '../src/pages/Home'
import Doctors from '../src/pages/Doctors'
import Login from '../src/pages/Login'
import About from '../src/pages/About'
import Contact from '../src/pages/Contact'
import MyProfile from '../src/pages/MyProfile'
import MyAppointment from '../src/pages/MyAppointment'
import Appointment from '../src/pages/Appointment'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
  import { ToastContainer, toast } from 'react-toastify';

const App = () => {
  return (
    <div className='mx-4 sm:mx-[10%]'>
        <Navbar />
        <ToastContainer />
        <Routes>
            <Route path='/' element={<Home />} />
            <Route path='/doctors' element={<Doctors />} />
            <Route path='/doctors/:speciality' element={<Doctors />} />
            <Route path='/login' element={<Login />} />
            <Route path='/about' element={<About />} />
            <Route path='/contact' element={<Contact />} />
            <Route path='/my-profile' element={<MyProfile />} />
            <Route path='/my-appointments' element={<MyAppointment />} />
            <Route path='/appointments/:docId' element={<Appointment />} />
        </Routes>
        <Footer />
    </div>
  )
}

export default App