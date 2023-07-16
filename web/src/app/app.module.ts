import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { InfiniteScrollModule } from 'ngx-infinite-scroll';
import {
  NbButtonModule,
  NbCalendarRangeModule,
  NbCardModule,
  NbContextMenuModule,
  NbDialogModule,
  NbIconModule,
  NbInputModule,
  NbLayoutModule,
  NbListModule,
  NbMenuModule,
  NbSelectModule,
  NbSidebarModule,
  NbSpinnerModule,
  NbTagModule,
  NbThemeModule,
  NbTooltipModule,
  NbTreeGridModule,
  NbUserModule,
} from '@nebular/theme';
import { NbEvaIconsModule } from '@nebular/eva-icons';
import { TimePastPipe } from 'ng-time-past-pipe';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { PostsGridComponent } from './posts-grid/posts-grid.component';
import { PostDetailComponent } from './post-detail/post-detail.component';
import { ProfileInfoComponent } from './profile-info/profile-info.component';
import { TaskStatusIconComponent } from './tasks/task-status-icon.component';
import { TaskTypeIconComponent } from './tasks/task-type-icon.component';

@NgModule({
  declarations: [
    AppComponent,
    PostsGridComponent,
    PostDetailComponent,
    ProfileInfoComponent,
    TaskStatusIconComponent,
    TaskTypeIconComponent,
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    InfiniteScrollModule,
    NbButtonModule,
    NbCalendarRangeModule,
    NbCardModule,
    NbContextMenuModule,
    NbDialogModule.forRoot(),
    NbIconModule,
    NbInputModule,
    NbLayoutModule,
    NbListModule,
    NbMenuModule.forRoot(),
    NbSelectModule,
    NbSidebarModule.forRoot(),
    NbSpinnerModule,
    NbTagModule,
    NbThemeModule.forRoot({ name: window.matchMedia("(prefers-color-scheme: dark)").matches ? 'dark' : 'default' }),
    NbTooltipModule,
    NbTreeGridModule,
    NbUserModule,
    NbEvaIconsModule,
    TimePastPipe,
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
