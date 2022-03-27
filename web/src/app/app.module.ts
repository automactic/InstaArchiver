import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { 
  NbActionsModule,
  NbCardModule,
  NbThemeModule, 
  NbLayoutModule, 
  NbListModule, 
  NbSidebarModule, 
  NbUserModule ,
  NbWindowModule,
} from '@nebular/theme';
import { NbEvaIconsModule } from '@nebular/eva-icons';
import { PostsComponent } from './posts/posts.component';
import { ProfileEditComponent } from './profile-edit/profile-edit.component';

@NgModule({
  declarations: [
    AppComponent,
    PostsComponent,
    ProfileEditComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    AppRoutingModule,
    NoopAnimationsModule,
    NbActionsModule,
    NbCardModule,
    NbThemeModule.forRoot({ name: 'default' }),
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
