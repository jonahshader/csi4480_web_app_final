import React from 'react'
import ReactDOM from 'react-dom/client'

import { create } from 'zustand'

import SignIn from 'src/pages/SignIn'
import SignUp from 'src/pages/SignUp'
import Dashboard from 'src/pages/dashboard/Dashboard'

import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import produce from 'immer'

export const useStore = create((set, get) => ({
  data: null,
  user_token: null,
  setUserToken: (user_token) => set({ user_token }),
  // fetchData uses user_token to retrieve data from the server
  fetchData: async () => {
    const user_token = get().user_token
    const response = await fetch('http://localhost:8000/data?user_token=' + user_token, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    const data = await response.json()

    if (data['token_expired']) {
      set({ user_token: null })
      set({ data: null })
    } else if (data['success']) {
      set({ data: data['user'] })
    } else {
      set({ data: null })
    }
  },
  
}))



export const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="/sign-in" />,
    errorElement: <div>404</div>,
  },
  {
    path: "/sign-in",
    element: <SignIn />,
  },
  {
    path: "/sign-up",
    element: <SignUp />,
  },
  {
    path: "/dashboard",
    element: <Dashboard />,
  }
]);


ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)
