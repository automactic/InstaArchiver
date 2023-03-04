import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {
  NbButtonModule,
  NbCardModule,
  NbDialogModule,
  NbIconModule,
  NbLayoutModule,
  NbListModule,
  NbSelectModule,
  NbSidebarModule,
  NbSpinnerModule,
  NbThemeModule,
  NbTooltipModule,
  NbUserModule,
} from '@nebular/theme';
import { NbEvaIconsModule } from '@nebular/eva-icons';
import { PostsGridComponent } from './posts-grid/posts-grid.component';
import { PostDetailComponent } from './post-detail/post-detail.component';

@NgModule({
  declarations: [
    AppComponent,
    PostsGridComponent,
    PostDetailComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    NbButtonModule,
    NbCardModule,
    NbDialogModule.forRoot(),
    NbIconModule,
    NbLayoutModule,
    NbListModule,
    NbSelectModule,
    NbSidebarModule.forRoot(),
    NbSpinnerModule,
    NbThemeModule.forRoot({ name: window.matchMedia("(prefers-color-scheme: dark)").matches ? 'dark' : 'default' }),
    NbTooltipModule,
    NbUserModule,
    NbEvaIconsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
