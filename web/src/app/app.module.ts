import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { 
  NbActionsModule,
  NbButtonModule,
  NbCardModule, 
  NbInputModule,
  NbLayoutModule, 
  NbListModule, 
  NbSidebarModule, 
  NbThemeModule,
  NbUserModule ,
  NbWindowModule,
} from '@nebular/theme';
import { NbEvaIconsModule } from '@nebular/eva-icons';
import { PostsComponent } from './posts/posts.component';
import { ProfileEditComponent } from './profile-edit/profile-edit.component';
import { ProfileDetailComponent } from './profile-detail/profile-detail.component';
import { PostsGridComponent } from './posts-grid/posts-grid.component';

@NgModule({
  declarations: [
    AppComponent,
    PostsComponent,
    ProfileEditComponent,
    ProfileDetailComponent,
    PostsGridComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,
    AppRoutingModule,
    NoopAnimationsModule,
    NbActionsModule,
    NbButtonModule,
    NbCardModule,
    NbInputModule,
    NbThemeModule.forRoot({ name: 'dark' }),
    NbWindowModule.forRoot({}),
    NbLayoutModule,
    NbListModule,
    NbSidebarModule.forRoot(),
    NbUserModule,
    NbEvaIconsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
