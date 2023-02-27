import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { PostsGridComponent } from './posts-grid/posts-grid.component';

const routes: Routes = [
  { path: 'posts', component: PostsGridComponent, pathMatch: 'full' },
  { path: ':username', component: PostsGridComponent, children: [
  ]},
  { path: '**', redirectTo: '/posts'},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
