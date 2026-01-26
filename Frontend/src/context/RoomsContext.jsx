import React, { createContext, useContext, useState, useEffect } from 'react';

const RoomsContext = createContext();

export const useRooms = () => {
  const context = useContext(RoomsContext);
  if (!context) {
    throw new Error('useRooms must be used within a RoomsProvider');
  }
  return context;
};

export const RoomsProvider = ({ children }) => {
  const [rooms, setRooms] = useState(() => {
    const savedRooms = localStorage.getItem('furniverse_rooms');
    if (!savedRooms) return [];
    
    try {
      const parsed = JSON.parse(savedRooms);
      // Migrate old data: filter out invalid products (legacy IDs instead of objects)
      return parsed.map(room => ({
        ...room,
        products: (room.products || []).filter(p => 
          typeof p === 'object' && p !== null && p.id && p.name
        )
      }));
    } catch (e) {
      console.error('Failed to parse rooms from localStorage:', e);
      return [];
    }
  });

  useEffect(() => {
    localStorage.setItem('furniverse_rooms', JSON.stringify(rooms));
  }, [rooms]);

  const addRoom = (roomData) => {
    const newRoom = {
      ...roomData,
      id: Date.now().toString(),
      createdAt: new Date().toISOString(),
      products: [], // Array to store product variant objects with full metadata
    };
    setRooms(prev => [...prev, newRoom]);
    return newRoom;
  };

  const updateRoom = (roomId, roomData) => {
    setRooms(prev =>
      prev.map(room =>
        room.id === roomId ? { ...room, ...roomData } : room
      )
    );
  };

  const deleteRoom = (roomId) => {
    setRooms(prev => prev.filter(room => room.id !== roomId));
  };

  const getActiveRoom = () => {
    return rooms.length > 0 ? rooms[0] : null;
  };

  const getRoomById = (roomId) => {
    return rooms.find(room => room.id === roomId) || null;
  };

  const addProductToRoom = (roomId, productData) => {
    setRooms(prev =>
      prev.map(room => {
        if (room.id === roomId) {
          const products = room.products || [];
          // Check if this exact variant is already in the room
          const variantKey = productData.variantId || productData.id;
          const exists = products.some(p => (p.variantId || p.id) === variantKey);
          
          if (exists) {
            return room;
          }
          
          // Store full product/variant data including color, price, images, metadata
          return {
            ...room,
            products: [...products, productData]
          };
        }
        return room;
      })
    );
  };

  const removeProductFromRoom = (roomId, productId, variantId = null) => {
    setRooms(prev =>
      prev.map(room => {
        if (room.id === roomId) {
          return {
            ...room,
            products: (room.products || []).filter(p => {
              const key = variantId || productId;
              const productKey = p.variantId || p.id;
              return productKey !== key;
            })
          };
        }
        return room;
      })
    );
  };

  const isProductInRoom = (roomId, productId, variantId = null) => {
    const room = rooms.find(r => r.id === roomId);
    if (!room?.products) return false;
    
    const key = variantId || productId;
    return room.products.some(p => (p.variantId || p.id) === key);
  };

  return (
    <RoomsContext.Provider
      value={{
        rooms,
        addRoom,
        updateRoom,
        deleteRoom,
        getActiveRoom,
        getRoomById,
        addProductToRoom,
        removeProductFromRoom,
        isProductInRoom,
      }}
    >
      {children}
    </RoomsContext.Provider>
  );
};
