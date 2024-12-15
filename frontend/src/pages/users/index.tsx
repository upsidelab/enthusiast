import { PageHeading } from "@/components/util/PageHeading.tsx";
import { PageMain } from "@/components/util/PageMain.tsx";
import { UsersList } from "@/components/users/users-list.tsx";

export function UsersIndex() {
  return (
    <PageMain>
      <PageHeading title="Manage Users" description="Create user accounts to give them access to data sets." />
      <UsersList />
    </PageMain>
  )
}
