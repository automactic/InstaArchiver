import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NbEvaIconsModule } from '@nebular/eva-icons';
import { 
  NbActionsModule, 
  NbButtonModule, 
  NbCardModule, 
  NbIconModule,
  NbInputModule, 
  NbLayoutModule, 
  NbListModule, 
  NbMenuModule, 
  NbSidebarModule, 
  NbThemeModule,
  NbUserModule,
} from '@nebular/theme';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { PostsComponent } from './posts/posts.component';
import { ArchiveComponent } from './archive/archive.component';
import { ProfilesComponent } from './profiles/profiles.component';
import { ProfileDetailComponent } from './profile-detail/profile-detail.component';


@NgModule({
  declarations: [
    AppComponent,
    ArchiveComponent,
    PostsComponent,
    ProfilesComponent,
    ProfileDetailComponent,
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    FontAwesomeModule,
    NbEvaIconsModule,
    NbActionsModule,
    NbButtonModule,
    NbCardModule,
    NbIconModule,
    NbInputModule,
    NbLayoutModule,
    NbListModule,
    NbMenuModule.forRoot(),
    NbSidebarModule.forRoot(),
    NbThemeModule.forRoot({ name: 'default' }), 
    NbUserModule,
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
