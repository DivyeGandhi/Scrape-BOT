import React, { useState } from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import DatasetView from './pages/DatasetView.jsx'
import { ReqdDataContext } from './context/ReqdDataContext.jsx'

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />
  },
  {
    path: '/dataset-view',
    element: <DatasetView />
  }
])

const Main = () => {
  const [reqdData, setReqdData] = useState({
    brand: "",
    flavor: "",
    website:"",
    list_of_prod:[
      {
        beverage_id:"NA",
        product_name:"NA",
        brand_name:"NA",
        flavor_name:"NA",
        price:"NA",
        discount:"NA",
        mrp:"NA",
        volume:"NA",
        quantity:"NA",
        location_name:"NA",
        website_name:"NA"
      }
    ]
  });

  return (
    <React.StrictMode>
      <ReqdDataContext.Provider value={{ reqdData, setReqdData }}>
        <RouterProvider router={router} />
      </ReqdDataContext.Provider>
    </React.StrictMode>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <Main />
)
