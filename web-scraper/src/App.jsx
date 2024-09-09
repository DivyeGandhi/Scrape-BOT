import './App.css';
import './index.css';
import SubmitForm from "./components/SubmitForm";
import { useState } from 'react';
import axios from 'axios';

function App() {

  return (
    <div className="flex flex-col items-center justify-center min-h-screen w-full bg-gray-100">
      <div className="flex flex-col items-center justify-center border-2 border-red-500 rounded-lg p-8 bg-white shadow-lg w-full max-w-md mx-4 my-10">
        <h1 className="text-2xl font-bold mb-6 text-red-600">Web Scraper</h1>
        <SubmitForm/>
      </div>
    </div>
  )
}

export default App;
