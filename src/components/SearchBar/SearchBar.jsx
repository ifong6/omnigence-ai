import { useState } from 'react'

const searchBar = () => {
  const [searchText, setSearchText] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const handleSearch = (e) => {
    setSearchText(e.target.value);

    if (!value.trim()) {
      setShowDropdown(false);
      setSearchResults([]);
      return;
    } 
    
    /*
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/search?query=${value}`);
      const data = await response.json();
      setSearchResults(data);
      setShowDropdown(true);
    } catch (error) {
      console.error('Error searching for quotations:', error);
    }
    */
  };


  return (
    <div>
      <p className="w-full felx px-10 py-2 text-2xl font-bold">Search Previous Quotation</p>
      <div className="w-full px-10 py-0 ">
        <input type="text" value={searchText} onChange={handleSearch}
          placeholder="Type in your quotation number or other quotation related messages...." 
          className="w-full px-4 py-2 border border-gray-300 rounded-lg flex items-center"
        />
      </div>
    </div>
  )
}




export default searchBar;