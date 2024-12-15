import { CreateDataSetForm } from "@/components/DataSets/CreateDataSetForm.tsx";
import { ApplicationContextProvider } from "@/components/util/ApplicationContextProvider.tsx";

export function OnboardingIndex() {
  return (
    <ApplicationContextProvider>
      <div className="flex flex-col items-center justify-center h-screen space-y-6 bg-gray-50 p-6">
        <div>
          <h1 className="text-lg font-medium mb-4">Create your first Data Set</h1>
          <CreateDataSetForm/>
        </div>
      </div>
    </ApplicationContextProvider>
  )
}
