import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import { createBrowserRouter, redirect, RouterProvider } from "react-router-dom";
import { History } from "@/pages/History.tsx";
import { Campaign } from "@/pages/Campaign.tsx";
import { Products } from "@/pages/Products.tsx";
import { Documents } from "@/pages/Documents.tsx";
import Login from "@/pages/Login.tsx";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { ApiConnection } from "@/pages/ApiConnection.tsx";
import { Docs } from "@/pages/Docs.tsx";
import { NoDataSets } from "@/pages/no-data-sets.tsx";
import { ApiClient } from "@/lib/api.ts";
import NewDataSet from "@/pages/data-sets/new.tsx";
import { DataSetsIndex } from "@/pages/data-sets";
import { IndexDataSetUsers } from "@/pages/data-sets/(id)/users.tsx";
import { UsersIndex } from "@/pages/users";
import { OnboardingIndex } from "@/pages/onboarding";
import { CreateServiceAccount } from "@/pages/CreateServiceAccount.tsx";

const api = new ApiClient(authenticationProviderInstance);

const protectedLoginLoader = async () => {
  if (!authenticationProviderInstance.isAuthenticated()) {
    return redirect("/login");
  }

  const apiDataSets = await api.dataSets().getDataSets();
  if (apiDataSets.length === 0) {
    const accountData = await api.getAccount();
    if (accountData.isStaff) {
      return redirect("/onboarding");
    } else {
      return redirect("/no-data-sets");
    }
  }

  return null;
};

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    loader: protectedLoginLoader,
    children: [
      {
        path: '/products',
        element: <Products />
      },
      {
        path: '/documents',
        element: <Documents />
      },
      {
        path: '/data-sets',
        element: <DataSetsIndex />
      },
      {
        path: '/data-sets/new',
        element: <NewDataSet />
      },
      {
        path: '/data-sets/:id/users',
        element: <IndexDataSetUsers />
      },
      {
        path: "/",
        element: <Campaign />
      },
      {
        path: '/ask/chat/:id?',
        element: <Campaign />
      },
      {
        path: '/ask/history',
        element: <History />
      },
      {
        path: '/api-connection',
        element: <ApiConnection />
      },
      {
        path: '/api-connection/new',
        element: <CreateServiceAccount />
      },
      {
        path: '/docs',
        element: <Docs />
      },
      {
        path: '/users',
        element: <UsersIndex />
      }
    ]
  },
  {
    path: "/login",
    element: <Login />
  },
  {
    path: "/no-data-sets",
    element: <NoDataSets />
  },
  {
    path: "/onboarding",
    element: <OnboardingIndex />
  }
]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
