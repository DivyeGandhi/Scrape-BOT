import React, { useContext, useState } from 'react'
import { brand_list, flavor_list, website_list } from "../beverage-list";
import { ReqdDataContext } from '../context/ReqdDataContext';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';


const SubmitForm = () => {
    const {reqdData, setReqdData} = useContext(ReqdDataContext);
    const navigate = useNavigate();

    const handleInputChange = (e) => {
        const{name, value} = e.target;

        console.log(name,value);

        setReqdData({
            ...reqdData,
            [name]: value
        })
    } 

    const sendRequest = async (e) => {
        e.preventDefault();
        if (!reqdData.brand) {
            return;
        }
        console.log(reqdData)
        try {
          const response = await axios.get('http://localhost:3000/beverages', {
            params: {
              brand: reqdData.brand,
              flavor: reqdData.flavor,
              website: reqdData.website
            },
            headers: {
              'Content-Type': 'application/json',
            }
          });    
          setReqdData({
            ...reqdData,
            list_of_prod: response.data
          })
          console.log(response.data)
          navigate("/dataset-view");
        } catch (error) {
          console.error('Error:', error);
        }
      }

    return (
        <div>
            <form className="w-full" onSubmit={sendRequest}>
                <div className="my-5">
                    <label className="block mb-2 font-semibold text-gray-700">Brand name</label>
                    <select
                        value={reqdData.brand}
                        name='brand'
                        className="w-full bg-gray-200 text-gray-700 rounded-full border-2 border-gray-300 py-2 px-4"
                        onChange={handleInputChange}
                    >
                        <option value=""></option>
                        {brand_list.map((item, index) => (
                            <option value={item} key={index}>{item}</option>
                        ))}
                    </select>
                </div>

                <div className="my-5">
                    <label className="block mb-2 font-semibold text-gray-700">Flavor</label>
                    <select
                        value={reqdData.flavor}
                        name='flavor'
                        className="w-full bg-gray-200 text-gray-700 rounded-full border-2 border-gray-300 py-2 px-4"
                        onChange={handleInputChange}
                    >
                        <option value=""></option>
                        {flavor_list.map((item, index) => (
                            <option value={item} key={index}>{item}</option>
                        ))}
                    </select>
                </div>

                <div className="my-5">
                    <label className="block mb-2 font-semibold text-gray-700">Website</label>
                    <select
                        value={reqdData.website}
                        name='website'
                        className="w-full bg-gray-200 text-gray-700 rounded-full border-2 border-gray-300 py-2 px-4"
                        onChange={handleInputChange}
                    >
                        <option value=""></option>
                        {website_list.map((item, index) => (
                            <option value={item} key={index}>{item}</option>
                        ))}
                    </select>
                </div>
                <button
                    className="w-full bg-blue-500 text-white font-bold py-2 px-4 rounded-full mt-4 hover:bg-blue-600 transition duration-200"
                    type="submit"
                >
                    Submit
                </button>
            </form>
        </div>
    )
}

export default SubmitForm