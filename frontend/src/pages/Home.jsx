import React from 'react'
import Header from '../components/Header'
import SpecialityMenu from '../components/SpecialityMenu'
import TopDoctors from '../components/TopDoctors'
import Banner from '../components/Banner'
import SymptomChecker from '../components/SymptomChecker'

const home = () => {
  return (
    <div>
      <Header />
      <SymptomChecker />
      <SpecialityMenu />
      <TopDoctors />
      <Banner />
    </div>
  )
}


export default home