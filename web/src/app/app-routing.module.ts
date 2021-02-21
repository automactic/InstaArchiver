import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { ArchiveComponent } from './archive/archive.component';
import { PostsComponent } from './posts/posts.component';

const routes: Routes = [
  { path: 'archive', component: ArchiveComponent },
  { path: 'posts', component: PostsComponent },
  { path: '',   redirectTo: '/archive', pathMatch: 'full' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
