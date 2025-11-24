import React, { useState, useEffect } from 'react';

const UserProfile = ({ userId }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser(userId);
  }, [userId]);

  const fetchUser = async (id) => {
    const response = await fetch(`/api/users/${id}`);
    const data = await response.json();
    setUser(data);
    setLoading(false);
  };

  const handleUpdate = () => {
    console.log('Update user');
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="profile">
      <h1>{user.name}</h1>
      <button onClick={handleUpdate}>Update</button>
    </div>
  );
};

export default UserProfile;
